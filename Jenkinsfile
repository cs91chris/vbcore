pipeline {
    agent {
        docker {
            image 'python:3.8.10'
        }
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '3'))
        timeout(time: 20, unit: 'MINUTES')
        ansiColor('xterm')
        timestamps()
    }

    stages {
        stage ('run tox') {
            steps {
                sh 'make run-tox'
            }
        }
        stage ('build') {
            steps {
                sh 'make build-dist'
            }
        }
    }

//     post {
//         always {}
//         success {}
//         failure {}
//         cleanup {
//             cleanWs()
//         }
//     }
}
