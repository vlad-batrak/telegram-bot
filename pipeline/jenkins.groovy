pipeline {
    agent any
    parameters {
        choice(name: 'OS', choices: ['linux', 'darwin', 'windows'], description: 'Pick OS')
        choice(name: 'ARCH', choices: ['amd64', 'arm64', 'armv7'], description: 'Pick ARCH')
    }
    environment {
        REPO    = 'https://github.com/vlad-batrak/telegram-bot'
        BRANCH  = 'main'
    }
    stages {
        stage('clone') {
            steps {
                echo "<<<<<<<<<<<<<<<<<<<<<<< CLONE REPO >>>>>>>>>>>>>>>>>>>>>>>>>>>"
                git branch: "${BRANCH}", url: "${REPO}"
            }
        }
        stage('test') {
            steps {
                echo "<<<<<<<<<<<<<<<<<<<<<<< TEST EXECUTING >>>>>>>>>>>>>>>>>>>>>>>>>>>"
                sh "make test"
            }
        }
        stage('build') {
            steps {
                echo "<<<<<<<<<<<<<<<<<<<<<<< BUILD EXECUTING >>>>>>>>>>>>>>>>>>>>>>>>>>>"
                sh "make build REGISTRY=${DOCKER_USER} TARGET_OS=${params.OS} TARGET_ARCH=${params.ARCH}"
            }
        }
        stage('image') {
            steps {
                echo "<<<<<<<<<<<<<<<<<<<<<<< IMAGE EXECUTING >>>>>>>>>>>>>>>>>>>>>>>>>>>"
                script {
                    sh "make image REGISTRY=${DOCKER_USER} TARGET_OS=${params.OS} TARGET_ARCH=${params.ARCH}"
                }
            }
        }
        stage('push') {
            steps {
                echo "<<<<<<<<<<<<<<<<<<<<<<< PUSH EXECUTING >>>>>>>>>>>>>>>>>>>>>>>>>>>"
                script {
                    docker.withRegistry('', 'dockerhub') {
                        sh "make push REGISTRY=${DOCKER_USER} TARGET_OS=${params.OS} TARGET_ARCH=${params.ARCH}"           	
                    }
                }
            }
        }
    }
    post {
        always {
            echo "<<<<<<<<<<<<<<<<<<<<<<< CLEAN EXECUTING >>>>>>>>>>>>>>>>>>>>>>>>>>>"
            sh "make clean REGISTRY=${DOCKER_USER} TARGET_OS=${params.OS} TARGET_ARCH=${params.ARCH}"
        }
        success {
            echo 'I succeeded!'
        }
        unstable {
            echo 'I am unstable :/'
        }
        failure {
            echo 'I failed :('
        }
        changed {
            echo 'Things were different before...'
        }
    }
}