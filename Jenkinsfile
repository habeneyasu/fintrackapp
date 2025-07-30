pipeline {
    agent any

    environment {
        // Docker configuration
        DOCKER_IMAGE_NAME = 'fin-track-api'
        COMPOSE_PROJECT_NAME = "fintrack_${BUILD_NUMBER}"
        
        // Use environment variables matching your docker.env
        DB_HOST = 'db'
        DB_PORT = '3306'
        DB_NAME = 'fintrack_docker'
        DB_USER = 'fintrack_user'
        DB_PASSWORD = 'userpass' // Directly using from your docker.env
        DB_ROOT_PASSWORD = 'rootpass' // As defined in your compose file
    }

    stages {
        stage('Prepare Environment') {
            steps {
                script {
                    // Verify Docker is available
                    sh 'docker --version'
                    
                    // Create docker.env file dynamically
                    sh '''
                    cat > ./configs/environments/docker.env <<EOF
                    DB_HOST=${DB_HOST}
                    DB_PORT=${DB_PORT}
                    DB_NAME=${DB_NAME}
                    DB_USER=${DB_USER}
                    DB_PASSWORD=${DB_PASSWORD}
                    ENVIRONMENT=dev
                    DEBUG=False
                    SECRET_KEY=supersecretkey123!
                    EOF
                    '''
                }
            }
        }

        stage('Build and Start') {
            steps {
                script {
                    sh """
                    docker-compose build
                    docker-compose up -d
                    
                    # Wait for DB to be ready
                    timeout 120s bash -c '
                        while ! docker-compose exec db mysqladmin ping -h localhost -u root -p${DB_ROOT_PASSWORD} --silent; do
                            sleep 5
                            echo "Waiting for DB..."
                        done
                    '
                    """
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    sh '''
                    # Run backend tests
                    docker-compose exec app pytest tests/ -v
                    
                    # Or test API endpoints directly
                    docker-compose exec app curl -X GET http://localhost:8000/api/health
                    '''
                }
            }
        }
    }

    post {
        always {
            sh 'docker-compose down -v --remove-orphans'
            sh 'docker image prune -f'
        }
    }
}