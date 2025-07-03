pipeline {
  agent any
  environment {
    DOCKER_REGISTRY = 'your-registry'
    K8S_CONFIG = credentials('k8s-config')  
  }
  stages {
    stage('Build & Test') {
      steps {
        sh 'docker build -t $DOCKER_REGISTRY/fintrack:latest .'
        sh 'docker-compose -f docker-compose.test.yml up -d --build'
        sh 'pytest tests/'
      }
      post {
        always {
          sh 'docker-compose -f docker-compose.test.yml down'
        }
      }
    }
    stage('Push to Registry') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'docker-creds', usernameVariable: 'USER', passwordVariable: 'PASS')]) {
          sh 'echo $PASS | docker login -u $USER --password-stdin $DOCKER_REGISTRY'
          sh 'docker push $DOCKER_REGISTRY/fintrack:latest'
        }
      }
    }
    stage('Deploy to K8s') {
      steps {
        sh 'kubectl apply -f k8s/ --kubeconfig $K8S_CONFIG'
      }
    }
  }
}