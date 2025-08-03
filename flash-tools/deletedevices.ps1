foreach ($dev in Get-PnpDevice -InstanceId "USB\VID_239A&PID_CAFE*") {

	pnputil /remove-device $dev.InstanceId 
}
foreach ($dev in Get-PnpDevice -InstanceId "USB\VID_2E8A&PID_0005*") {

	pnputil /remove-device $dev.InstanceId 
}

pnputil /scan-devices