import os
import glob
import subprocess
import string
import random
from flask import render_template, flash, redirect, url_for, send_from_directory
from flask import current_app
from werkzeug.utils import secure_filename
from xport import app
from xport.forms import LoginForm, SubmitGromacsForm, SubmitAmberForm


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/delete/<path:job_id>')
def delete_job(job_id):
    jobdir = os.path.join(app.config['UPLOAD_FOLDER'], job_id)
    files = glob.glob(os.path.join(jobdir, '*'))
    for file in files:
        os.remove(file)
    os.rmdir(jobdir)
    return redirect(url_for('jobs'))

@app.route('/stop/<path:job_id>')
def stop_job(job_id):
    joblist = get_jobs()
    for job in joblist:
        if job['job_id'] == job_id:
            if job['state'] == 'running':
                pid = subprocess.check_output('tsp -p {}'.format(job['index']), shell=True, universal_newlines=True)
                result2 = subprocess.check_output('kill -9 {}'.format(pid), shell=True, universal_newlines=True)
    return redirect(url_for('jobs'))
            
@app.route('/jobs/<path:job_id>')
def jobfiles(job_id):
    jobdir = os.path.join(app.config['UPLOAD_FOLDER'], job_id)
    result = subprocess.check_output(['ls', '-l', jobdir],
                                     universal_newlines=True)
    file_list = result.split('\n')[1:]
    files = []
    for file_data in file_list:
        fd = {}
        fields = file_data.split()
        if len(fields) == 9:
            fd['size'] = fields[4]
            fd['name'] = fields[8]
            fd['path'] = os.path.join(job_id, fields[8])
            files.append(fd)
    return render_template('jobfiles.html', title='Job {}'.format(job_id), files=files)

def get_jobs():
    jobdirs = glob.glob(os.path.join(app.config['UPLOAD_FOLDER'], '??????'))
    job_ids = [os.path.basename(j) for j in jobdirs]
    joblist = []
    result = subprocess.check_output('tsp', shell=True, universal_newlines=True)
    for line in result.split('\n')[1:]:
        words = line.split()
        if len(words) > 5:
            if words[1] == 'finished':
                command_indx = 5
            elif words[1] in ['running', 'queued']:
                command_indx = 3
            command = words[command_indx]
            if command[0] == '[' and command[7] == ']':
                job_id = command[1:7]
                state = words[1]
                if job_id in job_ids:
                    jobdict = {}
                    jobdict['job_id'] = job_id
                    jobdict['state'] = words[1]
                    jobdict['index'] = words[0]
                    joblist.append(jobdict)
    return joblist

@app.route('/jobs')
def jobs():
    joblist = get_jobs()
    joblist.reverse()
    tmplist = []
    for job in joblist:
        if job['state'] == 'running':
            tmplist.append(job)
    for job in joblist:
        if job['state'] == 'queued':
            tmplist.append(job)
    for job in joblist:
        if job['state'] == 'finished':
            tmplist.append(job)
    joblist = tmplist
    return render_template('jobs.html', title='Jobs', joblist=joblist)

@app.route('/downloads/<path:filename>', methods=['GET', 'POST'])
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename,
                               as_attachment=True)

@app.route('/display/<path:filename>', methods=['GET', 'POST'])
def display_file(filename):
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    with open(path, 'r') as text:
        content = text.read()
    return render_template('display.html', text=content.decode('utf-8'))
    
@app.route('/success')
def success():
    return render_template('success.html', title='Success')

def random_id(size):
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(size))

@app.route('/submit/amber', methods=['GET', 'POST'])
def submit_amber():
    form = SubmitAmberForm()
    if form.validate_on_submit():
        job_id = random_id(6)
        app.config['JOB_ID'] = job_id
        jobdir = os.path.join(app.config['UPLOAD_FOLDER'], job_id)
        os.mkdir(jobdir)

        mdinfile = form.mdinfile.data
        mdin_filename = secure_filename(mdinfile.filename)
        mdinfile.save(os.path.join(jobdir, mdin_filename))

        prmtopfile = form.prmtopfile.data
        prmtop_filename = secure_filename(prmtopfile.filename)
        prmtopfile.save(os.path.join(jobdir, prmtop_filename))

        inpcrdfile = form.inpcrdfile.data
        inpcrd_filename = secure_filename(inpcrdfile.filename)
        inpcrdfile.save(os.path.join(jobdir, inpcrd_filename))

        command = 'pmemd.cuda -i {} -c {} -p {}'.format(mdin_filename, inpcrd_filename, prmtop_filename)
        full_cmd = 'cd {} && tsp -L {} xflow-exec "{}"'.format(jobdir, job_id, command)
        result = subprocess.check_output(full_cmd, shell=True, universal_newlines=True)
        return render_template('success.html', result=result, job_id=job_id, filename=mdin_filename, title='Success')
    return render_template('submit_amber.html', form=form, title='Submit Amber Job')

@app.route('/submit/gromacs', methods=['GET', 'POST'])
def submit_gromacs():
    form = SubmitGromacsForm()
    if form.validate_on_submit():
        f = form.tprfile.data
        filename = secure_filename(f.filename)
        chars = string.ascii_lowercase + string.digits
        job_id = ''.join(random.choice(chars) for _ in range(6))
        app.config['JOB_ID'] = job_id
        jobdir = os.path.join(app.config['UPLOAD_FOLDER'], job_id)
        os.mkdir(jobdir)
        f.save(os.path.join(jobdir, filename))
        command = 'gmx mdrun -deffnm {}'.format(os.path.splitext(filename)[0])
        full_cmd = 'cd {} && tsp -L {} xflow-exec "{}"'.format(jobdir, job_id, command)
        result = subprocess.check_output(full_cmd, shell=True, universal_newlines=True)
        return render_template('success.html', result=result, job_id=job_id, filename=f.filename, title='Success')
    return render_template('submit_gromacs.html', form=form, title='Submit Gromacs Job')

@app.route('/cluster')
def cluster_info():
    result = subprocess.check_output('xflow-stat', shell=True, universal_newlines=True)
    workerlist = []
    indx = 0
    for line in result.split('\n')[1:]:
        words = line.split()
        if len(words) > 3:
            workerdict = {}
            workerdict['index'] = indx
            workerdict['executing'] = words[2]
            workerdict['in_memory'] = words[3]
            workerdict['ip_address'] = words[0]
            workerlist.append(workerdict)
            indx += 1
    result2 = subprocess.check_output('xflow-execall "curl -s http://169.254.169.254/latest/meta-data/instance-type"', shell=True, universal_newlines=True)
    for line in result2.split('\n'):
        words = line.split()
        if len(words) == 2:
            ip_address = words[1][:-1]
        elif len(words) == 1:
            instance_type = words[0]
            for worker in workerlist:
                if worker['ip_address'] == ip_address:
                    worker['instance_type'] = instance_type
            
    return render_template('cluster_info.html', title='Cluster info', workerlist=workerlist)
        
