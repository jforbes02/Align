HOW TO CONNECT BACKEND AND FRONTEND

STEP 1:

    Find your computers local ip. 
    On mac use
        ifconfig | grep "inet " | grep -v 127.0.0.1
    On windows use
        ipconfig

Step 2:

    In /local.properties replace BASE_URL=http://192.168.64.1:8000/
    with BASE_URL=http://your-ip:8000/

Step 3:

    Run
    