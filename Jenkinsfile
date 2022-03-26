pipeline {
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

    post {
        always {}
        success {}
        failure {}
        cleanup {
            cleanWs()
        }
    }
}
