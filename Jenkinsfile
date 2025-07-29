// Jenkinsfile for fin-track-api CI (Build & Test locally on Jenkins agent)
pipeline {
    agent any // Jenkins agent needs Docker and docker-compose installed

    environment {
        // --- Configuration for Docker Image (local build only) ---
        // The image will be built and available locally on the Jenkins host.
        DOCKER_IMAGE_NAME = 'fin-track-api' // Name for your application's Docker image

        // --- GitHub Repository Credentials (for Jenkins Checkout) ---
        // This credential should be an 'SSH Username with Private Key' type in Jenkins.
        // Make sure its ID matches what you set in Jenkins Credentials.
        GITHUB_SSH_CREDENTIAL_ID = 'github-jenkins-ssh' // <<=== REPLACE WITH YOUR GITHUB SSH CREDENTIAL ID IN JENKINS
    }

    stages {
        stage('Checkout Source Code') {
            steps {
                echo "Cloning GitHub repository: git@github.com:your-github-username/fin-track-api.git"
                // Clones your fin-track-api GitHub repository
                git branch: 'main', credentialsId: "${GITHUB_SSH_CREDENTIAL_ID}", url: 'git@github.com:your-github-username/fin-track-api.git' // <<=== REMEMBER TO REPLACE 'your-github-username'
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    // Build the Docker image for your 'app' service using the Dockerfile in the root.
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
                // Ensure docker-compose.test.yml correctly defines services needed for testing (app_test, db_test).
                echo "Spinning up test environment with docker-compose.test.yml..."
                sh 'docker-compose -f docker-compose.test.yml up -d --build --force-recreate' // --force-recreate ensures fresh containers

                // IMPORTANT: Wait for services (especially DB) to be healthy before running tests.
                // Adjust this sleep or implement a proper 'wait-for-it' mechanism.
                echo "Waiting 30 seconds for services to become healthy..."
                sh 'sleep 30'

                // Run your Python tests. Pytest needs to be able to connect to the app/db services.
                echo "Running pytest tests..."
                sh 'pytest tests/' // <<=== ENSURE 'pytest' is runnable in your test environment
            }
            post {
                always {
                    // Always tear down the test environment after tests run (or fail)
                    echo "Tearing down test environment..."
                    sh 'docker-compose -f docker-compose.test.yml down'
                }
            }
        }
        // The 'Push Docker Image to Registry' stage is removed as per your request.
        // The 'Deploy' stage will be discussed separately once this CI pipeline is successful.
    }
}