// Jenkinsfile for FinTrack API CI/CD
// This pipeline builds the Docker image, runs tests, and optionally deploys locally.
pipeline {
    agent any // Jenkins agent needs Docker, docker-compose, and access to Docker daemon.

    environment {
        // --- Docker Image Configuration ---
        DOCKER_IMAGE_NAME = "habeneyasu/fintrackapp" // Your Docker image name/repository
        # This will be replaced from the job 
        # TAG = "latest" // You can use a fixed tag or dynamic like BUILD_NUMBER
    }

    stages {
        // The 'Clone Repo' stage is REMOVED.
        // Jenkins automatically checks out the source code at the start of the pipeline.
        // Your code will be available in the workspace: /var/jenkins_home/workspace/fintrack-api-pipeline/

        stage('Build Docker Image') {
            steps {
                script {
                    echo "Building Docker image: ${DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER}"
                    // Build with BUILD_NUMBER tag
                    sh "docker build -t ${DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER} ."
                    // Also tag with 'latest' for convenience
                    sh "docker tag ${DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER} ${DOCKER_IMAGE_NAME}:latest"
                }
            }
        }

        stage('Run Integration Tests') {
            steps {
                echo "Spinning up test environment with docker-compose.test.yml..."
                // Use docker-compose.test.yml for testing environment
                sh 'docker-compose -f docker-compose.test.yml up -d --build --force-recreate'

                // Important: Wait for services (especially the database) to be healthy
                echo "Waiting 30 seconds for services to become healthy..."
                sh 'sleep 30' // Adjust this sleep duration as needed

                echo "Running pytest tests..."
                sh 'pytest tests/' // Make sure 'pytest tests/' runs your tests correctly
            }
            post {
                always {
                    echo "Tearing down test environment..."
                    sh 'docker-compose -f docker-compose.test.yml down' // Clean up containers after tests
                }
            }
        }

        stage('Deploy Application (Local Jenkins Host)') {
            steps {
                script {
                    echo "Stopping and removing existing container (if any)..."
                    // Stop and remove old container
                    sh 'docker stop fintrack-api || true' // '|| true' prevents pipeline failure if container doesn't exist
                    sh 'docker rm fintrack-api || true'

                    echo "Running new application container: ${DOCKER_IMAGE_NAME}:latest"
                    // Run the new container from the 'latest' tagged image
                    sh "docker run -d -p 8000:8000 --name fintrack-api ${Docker_IMAGE_NAME}:latest"
                    echo "Application should now be running on port 8000 of the Jenkins host."
                }
            }
        }
        // No 'Push Docker Image' stage as per your current setup.
        // No Kubernetes deployment yet.
    }
}
