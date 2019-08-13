pipeline {
    agent any
    stages {
        stage('anvironment.build') {
            steps {
                sh 'ls'
                sh 'pip install virtualenv '
                sh 'virtualenv -p $(which python) .venv'
                sh 'source .venv/bin/activate'
            }
        }
    }
    post {
        always {
            echo 'One way or another, I have finished and I will cleanup environement'
            deleteDir() /* clean up our workspace */
        }
        success {
            echo 'I succeeeded!'
        }
        unstable {
            echo 'I am unstable :/'
        }
        failure {
            echo 'I failed :('
        }
        changed {
            echo 'Things were different before...'
        }
    }
}