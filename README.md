# khmer-license-plate-recognition

<img src="https://lh3.googleusercontent.com/pw/ADCreHcffclef1XQF2m53SC2MKyOGCFhkbeLJqT3UIN2iHMFerDcbps8hn4gkRRjz3TSgyEeD0PL2bzVNPidIeojV2IeImRVcolZ_imXT0lkTKVea9kZNEfD5gAMxFnyWjaaZrAI2PDGP7WRSCf40tcNrFBD=w1579-h963-s-no">

Clone the project to your local machine. I recomment you to clone it using vs code terminal since it will ask you to put your credential and github have removed their access credential from the terminal.

        git clone https://github.com/nattkorat/khmer-license-plate-recognition.git


### Install Dependencies

You can install all dependencie on you local machine, but to avoid the conflic with other project dependencies you should create a virtual environment.

On your terminal install the dependencies from requirements.txt

        pip install -r requirements.txt

### Download Models

You have to create a folder "models" to store our model. You can run this commandd in your terminal to create folder and move your current directory to it.

        mkdir models

You need to download all the models from the drive and store it in that `models` directory. <a href="https://cadtedu-my.sharepoint.com/:f:/g/personal/korat_natt_cadt_edu_kh/Et6APpp0NwlHkmpuS0XCkpYBiCNNwtHFhyCpIqZI-sKH7A?e=XxC4C1" target="_blank">Download Model</a>


### Testing 

After everything is completed, you can test this project by run the python script as below (just testing with the dev api):

    python app.py


On your favorite browser, you can access this by your localhost

    http://localhost:5000/

Or on other machine, it can access by your ip address follow by the the same port. For example my ip address is 192.168.0.1, so I can access this on other computer by

    http://192.168.0.1:5000/

On the detection processing script is in the "util/extract.py" file.

### Testing with video

