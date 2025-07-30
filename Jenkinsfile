// Jenkinsfile for fin-track-api CI (Build & Test with Docker-in-Docker approach)
pipeline {
    agent {
        docker {
            image 'docker:24.0-dind'  // Uses Docker-in-Docker with latest stable version
            args '--privileged -v /var/run/docker.sock:/var/run/docker.sock'
        }
    }

    environment {
        DOCKER_IMAGE_NAME = 'fin-track-api'
        COMPOSE_PROJECT_NAME = 'fintrack_ci_${BUILD_NUMBER}'  // Isolates containers per build
    }

    stages {
        stage('Build Docker Image') {
            steps {
                script {
                    echo "Building Docker image: ${DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER}"
                    
                    // Install docker-compose v2 (compose-plugin) if needed
                    sh '''
                        apk add --no-cache docker-cli-compose
                        docker compose version
                    '''
                    
                    // Build with BuildKit for better performance
                    sh "DOCKER_BUILDKIT=1 docker build -t ${DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER} ."
                    sh "docker tag ${DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER} ${DOCKER_IMAGE_NAME}:latest"
                }
            }
        }

        stage('Run Integration Tests') {
            steps {
                script {
                    echo "Starting test environment..."
                    sh '''
                        docker compose -f docker-compose.test.yml up -d --build
                        
                        # Wait for DB to be ready (better than sleep)
                        timeout 60s bash -c 'until docker compose -f docker-compose.test.yml exec db mysqladmin ping -h localhost -u root -prootpass; do sleep 2; done'
                    '''
                    
                    echo "Running tests..."
                    sh '''
                        docker compose -f docker-compose.test.yml exec app_test pytest tests/ -v
                    '''
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
            // Clean up any dangling images
            sh 'docker image prune -f'
        }
    }
}