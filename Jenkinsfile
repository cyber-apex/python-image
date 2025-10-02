pipeline {
    agent any
    
    environment {
        PROJECT_NAME = 'python-image'
        DEPLOY_PATH = '/opt/python-image'
        PYTHON_BIN = '/usr/local/bin/python3.9'
        VENV_PATH = "${DEPLOY_PATH}/venv"
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out code...'
                checkout scm
            }
        }
        
        stage('Install Dependencies') {
            steps {
                echo 'Installing dependencies...'
                sh '''
                    ${PYTHON_BIN} -m venv ${WORKSPACE}/venv
                    . ${WORKSPACE}/venv/bin/activate
                    python --version
                    pip --version
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }
        
        stage('Test') {
            steps {
                echo 'Running tests...'
                sh '''
                    . ${WORKSPACE}/venv/bin/activate
                    # Add your test commands here
                    python -c "import flask; import PIL; print('Dependencies OK')"
                '''
            }
        }
        
        stage('Deploy') {
            steps {
                echo 'Deploying application...'
                sh '''
                    # Create deploy directory if not exists
                    sudo mkdir -p ${DEPLOY_PATH}
                    sudo mkdir -p /var/log/supervisor
                    
                    # Copy application files
                    sudo cp -r ${WORKSPACE}/* ${DEPLOY_PATH}/
                    
                    # Create/update virtual environment
                    sudo ${PYTHON_BIN} -m venv ${VENV_PATH}
                    sudo ${VENV_PATH}/bin/pip install --upgrade pip
                    sudo ${VENV_PATH}/bin/pip install -r ${DEPLOY_PATH}/requirements.txt
                    
                    # Copy supervisor config
                    sudo cp ${DEPLOY_PATH}/python-image.ini /etc/supervisord.d/
                    
                    # Reload and restart supervisor service
                    sudo supervisorctl reread
                    sudo supervisorctl update
                    sudo supervisorctl restart python-image-gunicorn
                '''
            }
        }
        
        stage('Health Check') {
            steps {
                echo 'Checking application health...'
                sh '''
                    sleep 5
                    curl -f http://localhost:5566/health || exit 1
                '''
            }
        }
    }
    
    post {
        success {
            echo 'Deployment successful!'
        }
        failure {
            echo 'Deployment failed!'
            // Add notification steps here (email, Slack, etc.)
        }
        always {
            cleanWs()
        }
    }
}

