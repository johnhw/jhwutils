import zipfile, os, datetime
import sys

if (sys.version_info < (3, 0)):
    print("Make sure you are using the correct Python (try using /usr/local/anaconda3/python)")
    print("No output generated")
    sys.exit(-1)

    
print("Creating submission.zip")
print("Generating/updating submission zipfile on %s" % datetime.datetime.now())
with zipfile.ZipFile("submission.zip", "w", zipfile.ZIP_DEFLATED) as zip:
    print("Including notebooks:")
    for root, dirs, files in os.walk('.'):        
        zip.write(root, os.path.relpath(root, '.'))
        for file in files:            
            filename = os.path.join(root, file)            
            if os.path.isfile(filename) and not filename.endswith('.zip') and not "ipynb_checkpoints" in filename:
                name = os.path.join(os.path.relpath(root, '.'), file)
                zip.write(filename, name)            
                if os.path.isfile(filename) and filename.endswith('.ipynb'):
                    print("\t\t%s" % filename)
                
print("Complete! You can submit submission.zip on Moodle")