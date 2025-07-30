// Jenkinsfile for FinTrack API CI/CD
// This pipeline builds the Docker image, runs tests, and optionally deploys locally.
pipeline {
    agent any // Jenkins agent needs Docker, docker-compose, and access to Docker daemon.

    environment {
        // --- Docker Image Configuration ---
        DOCKER_IMAGE_NAME = "habeneyasu/fintrackapp" // Your Docker image name/repository
        // This will be replaced from the job
        // TAG = "latest" // You can use a fixed tag or dynamic like BUILD_NUMBER
    }

    stages {
        stage('Build Docker Image') {
            steps {
                script {
                    // --- Diagnostic Steps (KEEP THESE!) ---
                    echo "Checking for Docker executable path..."
                    sh 'which docker || echo "docker not found in PATH, trying /usr/bin/docker"' // Check if docker is found
                    sh '/usr/bin/docker info || echo "Could not get docker info from /usr/bin/docker"' // Use absolute path for info

                    // Set PATH for current shell to include /usr/bin
                    // Alternatively, you can use the full path '/usr/bin/docker' in each command below.
                    sh 'export PATH="/usr/bin:$PATH"' 
                    echo "PATH updated for current shell."

                    // --- End Diagnostic Steps ---

                    echo "Building Docker image: ${DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER}"
                    sh "docker build -t ${DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER} ." // Now 'docker' should work
                    sh "docker tag ${DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER} ${DOCKER_IMAGE_NAME}:latest"
                }
            }
        }

        stage('Run Integration Tests') {
            steps {
                // Ensure docker-compose is also accessible if it's installed via apt
                sh 'export PATH="/usr/bin:$PATH"'
                echo "Spinning up test environment with docker-compose.test.yml..."
                sh 'docker-compose -f docker-compose.test.yml up -d --build --force-recreate'

                echo "Waiting 30 seconds for services to become healthy..."
                sh 'sleep 30'

                echo "Running pytest tests..."
                sh 'pytest tests/'
            }
            post {
                always {
                    echo "Tearing down test environment..."
                    sh 'docker-compose -f docker-compose.test.yml down'
                }
            }
        }

        stage('Deploy Application (Local Jenkins Host)') {
            steps {
                script {
                    sh 'export PATH="/usr/bin:$PATH"'
                    echo "Stopping and removing existing container (if any)..."
                    sh 'docker stop fintrack-api || true'
                    sh 'docker rm fintrack-api || true'

                    echo "Running new application container: ${DOCKER_IMAGE_NAME}:latest"
                    sh "docker run -d -p 8000:8000 --name fintrack-api ${DOCKER_IMAGE_NAME}:latest"
                    echo "Application should now be running on port 8000 of the Jenkins host."
                }
            }
        }
    }
}
