pipeline {
    agent any

    environment {
        COMPOSE_PROJECT_NAME = 'fintrack'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    sh 'docker-compose build app'
                }
            }
        }

        stage('Start Services') {
            steps {
                script {
                    // Run docker-compose up in detached mode
                    sh 'docker-compose up -d'
                }
            }
        }

        stage('Health Check / Wait for Services') {
            steps {
                script {
                    // Wait for DB or app to be healthy (optional)
                    sh 'sleep 10'  // or custom health check logic
                }
            }
        }

        // Optional test stage
        stage('Run Tests') {
            steps {
                echo 'Running tests (if any)'
                // You can add: sh 'docker-compose exec app pytest'
            }
        }

    }

    post {
        always {
            echo 'Stopping Docker containers'
            sh 'docker-compose down'
        }
    }
}
