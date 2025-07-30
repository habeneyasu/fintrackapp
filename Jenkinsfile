pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE_NAME = 'fin-track-api'
        COMPOSE_PROJECT_NAME = "fintrack_${BUILD_NUMBER}"
    }

    stages {
        stage('Setup Environment') {
            steps {
                script {
                    // Verify/install Docker
                    sh '''
                        if ! command -v docker &> /dev/null; then
                            echo "Installing Docker..."
                            curl -fsSL https://get.docker.com | sh
                            sudo usermod -aG docker jenkins
                            sudo systemctl restart docker
                        fi
                        
                        # Verify Docker access
                        docker --version
                    '''
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    echo "Building Docker image: ${DOCKER_IMAGE_NAME}:${BUILD_NUMBER}"
                    sh """
                        docker build -t ${DOCKER_IMAGE_NAME}:${BUILD_NUMBER} .
                        docker tag ${DOCKER_IMAGE_NAME}:${BUILD_NUMBER} ${DOCKER_IMAGE_NAME}:latest
                    """
                }
            }
        }

        stage('Run Integration Tests') {
            steps {
                script {
                    echo "Starting test environment..."
                    sh """
                        docker compose -f docker-compose.test.yml up -d --build
                        
                        # Wait for DB to be ready
                        timeout 120s bash -c 'until docker compose -f docker-compose.test.yml exec db mysqladmin ping -h localhost -u root -prootpass; do sleep 5; done'
                        
                        # Run tests
                        docker compose -f docker-compose.test.yml exec app_test pytest tests/ -v
                    """
                }
            }
            post {
                always {
                    echo "Cleaning up test environment..."
                    sh 'docker compose -f docker-compose.test.yml down -v --remove-orphans'
                }
            }
        }
    }

    post {
        always {
            echo "Pipeline completed - cleaning up"
            sh 'docker image prune -f'
            // Optional: Archive test results if using JUnit reports
            // junit '**/test-reports/*.xml' 
        }
    }
}