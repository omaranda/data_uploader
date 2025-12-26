Context: We deploy audio recorders audible and ultrasonic and camera trap in the field in many countries and we collect the files each quarter of the year or each month, we need to upload the files into an S3 bucket, each bucket is related with one project.

each project has 3 to 5 cycles called C1,C2,C3, etc per project

and inside each cycle we use the serial number of the sensor as a foldername with all the wav files or images, videos.

We have clients as a companies and each client has one or more projects and each company has one or more users.

Can you helpe me to create a CLI appliction in python to read a source path to upload all WAV, JPG and VIDEO files into an S3 aws bucket.

the idea is to read .aws/credentials and use python to read the origin path with python or explore it with command find for linux and os users. and or use aws command line I don't know wich one is faster.

please create a database in postgresql to store:

- project name / bucket name
- preffix, the preffix correspond to a cycle (C1,C2,C3, etc)
- list of files to be uploaded asociated with each bucket name
- use that list to track the status of the file if it was succesfuly uploaded or not because it's important to support resume 
- as part of the configuration i want to define how many times should retry the script to upload the failed files automatically 
- once all the files were uploaded the tool should call an endpoint to register into our system to trigger the automated processing.

in a directory called config_files i would like to store a json file of each delivery 

{
    "local_directory": "be-ki-leuchttuerme-lbr-data",
    "bucket_name": "be-ki-leuchttuerme-lbr-data",
    "s3_prefix": "C2",
    "max_workers": 15,
    "aws_region": "eu-west-1",
    "times_to_retry": 3,
    "aws_profile": "aws-eos"
    "use_find": "yes" # or no to use python considering windows machines 
}

and store the config on the database but it's important to support flags from the command line

I would like to see in the terminal as part of the output of the command:

something silimar to this output:

Sync Session ID: 30 (from the DB)
🔄 Auto-retry enabled: 3 attempts with 5s delay
✅ Verified directory: /Volumes/BW_2025_1/be-ki-leuchttuerme-lbr-data/c2
✅ Using AWS profile: aws-eos
✅ AWS Identity: arn:aws:iam::752715377980:user/be_omar
🔍 Verifying access to bucket: be-ki-leuchttuerme-byw-data
✅ Bucket access verified: be-ki-leuchttuerme-byw-data
✅ Bucket listing permissions verified
✅ Prefix structure already exists: C2
🔍 Analyzing files for sync...
⚡ Using native find command for maximum speed...
🔍 Loading S3 bucket file list...
✅ Loaded 344,271 files from S3 cache
📋 Loading previously uploaded files from database...
✅ Loaded 344,265 previously uploaded files into cache
📁 Scanning local directory...
   ⚡ find: Found 10,000 files so far...
   ⚡ find: Found 20,000 files so far...
   ⚡ find: Found 30,000 files so far...
   ⚡ find: Found 40,000 files so far...
   ⚡ find: Found 50,000 files so far...
   ⚡ find: Found 60,000 files so far...
   ⚡ find: Found 70,000 files so far...
   ⚡ find: Found 80,000 files so far...
   ⚡ find: Found 90,000 files so far...
   ⚡ find: Found 100,000 files so far...
   ⚡ find: Found 110,000 files so far...
   ⚡ find: Found 120,000 files so far...
   ⚡ find: Found 130,000 files so far...
   ⚡ find: Found 140,000 files so far...
   ⚡ find: Found 150,000 files so far...
   ⚡ find: Found 160,000 files so far...
   ⚡ find: Found 170,000 files so far...
   ⚡ find: Found 180,000 files so far...
   ⚡ find: Found 190,000 files so far...
   ⚡ find: Found 200,000 files so far...
   ⚡ find: Found 210,000 files so far...
   ⚡ find: Found 220,000 files so far...
   ⚡ find: Found 230,000 files so far...
   ⚡ find: Found 240,000 files so far...
   ⚡ find: Found 250,000 files so far...
   ⚡ find: Found 260,000 files so far...
   ⚡ find: Found 270,000 files so far...
   ⚡ find: Found 280,000 files so far...
   ⚡ find: Found 290,000 files so far...
   ⚡ find: Found 300,000 files so far...
   ⚡ find: Found 310,000 files so far...
   ⚡ find: Found 320,000 files so far...
   ⚡ find: Found 330,000 files so far...
   ⚡ find: Found 340,000 files so far...
💾 Saving file analysis to database...
✅ Saved 5 file records to database
📝 Note: 344,265 files were already uploaded in previous sessions and were excluded from this sync

⚡ Performance Summary:
   • Total files scanned: 344,270
   • Scan time: 2394.9s (144 files/sec)
   • Database save time: 0.2s
   • Total analysis time: 2499.9s

==========================================================================================
🚀 SMART S3 SYNC UPLOADER (DATABASE VERSION)
==========================================================================================
📁 Total local files: 5
💾 Total local size: 0.06 GB
✅ Files already in S3: 5
🔄 Files to upload: 0
📦 S3 Destination: s3://be-ki-leuchttuerme-byw-data/C2
📊 Database Session ID: 30
==========================================================================================
🎉 All files are already synced with S3!

- progress bar | 84.9% | Uploaded: 256,097/301,575 | Skipped: 0 | Size: 2128.24 GB | Successful: 243,436 | Failed: 12,661 | Speed: 0.6 archivos/s | ETA: 20:57:

the progress bar should be display only once and avoid new lines on each update

probably it's a good idea to create one script for:
- upload files
- retry failed files
- call end point to register the files into redpanda
- create a master script to run the full pipeline

later create some SQL to use in grafana to know:

- total files per project / bucket as a table
- stauts up the uploading per project as a table
- a bar chart to compare cycle by cycle in quantity of files by type by bucket
- and all the general stats of the status of the files

create a doc folder to store all the documentation and quick guide

create the model for the database and the database should run in a docker image

do you think it's a good idea to use kafka? 

