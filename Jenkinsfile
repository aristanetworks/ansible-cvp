pipeline {
  agent any
  stages {
    stage('') {
      steps {
        sh '''pip install virtualenv
virtualenv -p $(which python) .venv
source .venv/bin/activate
pip install -r requirements.txt
ansible --version
ls .venv/lib/python2.7/site-packages/cvprac/
cp CVPRACv2/* .venv/lib/python2.7/site-packages/cvprac/'''
      }
    }
  }
}