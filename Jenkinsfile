pipeline {
    agent {
      docker {
        image 'inetsix/docker-ansible:2.7'
      }
    }
    stages {
        stage('environment.build') {
            steps {
                sh 'ls -l'
                sh 'pip install -r requirements.txt'
            }
        }
        stage('environment.validate') {
            steps {
                sh 'python --version'
                sh 'ansible --version'
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