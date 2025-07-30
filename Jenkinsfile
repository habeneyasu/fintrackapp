// Jenkinsfile for fin-track-api CI (Build & Test locally on Jenkins agent)
// This pipeline assumes the repository is checked out by the Jenkins job configuration itself.
pipeline {
    agent any // Jenkins agent needs Docker and docker-compose installed, and access to Docker daemon

    environment {
        // --- Configuration for Docker Image (built locally on Jenkins host) ---
        DOCKER_IMAGE_NAME = 'fin-track-api' // Name for your application's Docker image
    }

    stages {
        // The 'Checkout Source Code' stage is REMOVED from here.
        // Jenkins already performs the checkout automatically at the start of the pipeline
        // based on the SCM configuration in your Jenkins job settings.
        // The code will be available in the workspace: /var/jenkins_home/workspace/fin-track-api-pipeline/

        stage('Build Docker Image') {
            steps {
                script {
                    // Build the Docker image for your 'app' service using the Dockerfile in the root of the checked-out repository.
                    // This image will only exist locally on the Jenkins host after this step.
                    echo "Building Docker image: ${DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER}"
                    docker.build("${DOCKER_IMAGE_NAME}:${env.BUILD_NUMBER}", ".")
                    docker.build("${DOCKER_IMAGE_NAME}:latest", ".") // Also tag as latest locally
                }
            }
        }

        stage('Run Integration Tests') {
            steps {
                // Use your docker-compose.test.yml to spin up services for integration testing.
                // Ensure docker-compose.test.yml correctly defines services needed for testing (e.g., app_test, db_test).
                echo "Spinning up test environment with docker-compose.test.yml..."
                sh 'docker-compose -f docker-compose.test.yml up -d --build --force-recreate' // --force-recreate ensures fresh containers

                // IMPORTANT: Wait for services (especially the database) to be healthy before running tests.
                // Adjust this sleep duration (in seconds) as needed, or implement a more robust 'wait-for-it' mechanism.
                echo "Waiting 30 seconds for services to become healthy..."
                sh 'sleep 30'

                // Run your Python tests using pytest.
                // Ensure 'pytest' is runnable in your test environment (e.g., installed in your Dockerfile, or available on the Jenkins agent).
                echo "Running pytest tests..."
                sh 'pytest tests/'
            }
            post {
                always {
                    // Always tear down the test environment after tests run (or if they fail) to clean up resources.
                    echo "Tearing down test environment..."
                    sh 'docker-compose -f docker-compose.test.yml down'
                }
            }
        }
        // The 'Push Docker Image to Registry' stage is still removed as you indicated you are not using a registry for now.
        // The 'Deploy' stage will be discussed separately once this CI pipeline (Build and Test) is successful.
    }
}