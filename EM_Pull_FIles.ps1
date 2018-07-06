# Script for the EM group to copy files off the local hard-drive of the data-gathering
# PCs to an external hard-drive. This hard-drive will have a fixed drive letter.

function EM_Pull_Files {

# Recursively get all the child items in the source directory where the last write 
# time is more than 10 minutes ago, then move that to the target directory.

# First check if drive G: exists. If not, map it using the supplied credentials
if (!(Test-Path G:))
{
$net = new-object -ComObject WScript.Network
$net.MapNetworkDrive("G:", "\\gatancustomer\DoseFractions", $false, "gatancustomer\valuedgatancustomer", "`$admin")
}


# Create a variable that defines the source directory
$source = "G:\"

# Create a variable that defines the target directory
$destination = "D:\DoseFractions\"


# Now select all files that were last written to more than 10 minutes ago and copy them
# to the target destination. As we're being selective about files using Get-ChildItem,
# the Copy-Item command won't preserve the directory structure, so we have to run tests
# and create the correct directory structure if necessary.

# Create a variable that will hold the output from a Get-ChildItem call
$items = Get-ChildItem $source -Recurse -Filter "*_Data_*.mrc" | Where {$_.LastWriteTime -lt (Date).AddMinutes(-10)}

# Now run test commands on each item called from the Get-ChildItem commnad above
    foreach ($item in $items)
    {
# Create a variable to hold the name of the target directory (this takes the directory 
# name of the source file and replaces the source root directory info with the target
# root directory info
               $dir = $item.DirectoryName.Replace($source,$destination)

# Create a variable to hold the name of the target file name (this takes the full file 
# name of the source file and replaces the source root directory info with the target
# root directory info
               $target = $item.FullName.Replace($source,$destination)
 
# Test if the target directory exists. If not, create it
                if (!(test-path($dir))) { mkdir $dir }
 
# Test if the target file exists. If not, copy the source file across
        if (!(test-path($target)))
        {
            Move-Item -path $item.FullName -destination $target -force
        }
    }

#Get-ChildItem -recurse $source |
#Where {$_.LastWriteTime -lt (Date).AddMinutes(-10)} |
#Copy-Item -Destination $destination -Recurse -Force



} # End of function EM_Pull_Files


# Run the function EM_Pull_Files
EM_Pull_Files
