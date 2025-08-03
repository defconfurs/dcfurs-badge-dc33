These are some tools to help flash a lot of badges.

deletedevices.ps1 - Script to delete all the device nodes created by flashing badges, run this perodically so that you don't accumulate too many device nodes.  This will need to be run in an elevated PowerShell window, rightclick PowerShell and Run as Administrator.
flashbadge.ps1 - Script that looks for the INFO_UF2.TXT file in the root of the UF2 bootloader filesystem and then writes the uf2 file to it.   You will want to modify the drive letter and location of the file to be copied to suit your setup.

If you get an error that powerShell scripts cannot be executed due to policy, you will want to use this command to reset the policy:
Set-ExecutionPolicy -ExecutionPolicy Unrestricted

