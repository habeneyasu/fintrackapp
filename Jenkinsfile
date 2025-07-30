pipeline {
    agent any

    environment {
        IMAGE_NAME = "habeneyasu/fintrackapp"
        TAG = "latest"
    }

    stages {
        stage('Clone Repo') {
            steps {
                git branch: 'main', url: 'https://github.com/habeneyasu/fintrackapp.git'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    sh 'docker build -t $IMAGE_NAME:$TAG .'
                }
            }
        }

        stage('Run Container') {
            steps {
                script {
                    // stop old container if exists
                    sh 'docker stop fintrack-api || true'
                    sh 'docker rm fintrack-api || true'

                    // run new container
                    sh 'docker run -d -p 8000:8000 --name fintrack-api $IMAGE_NAME:$TAG'
                }
            }
        }
    }
}
