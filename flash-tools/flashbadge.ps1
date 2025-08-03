for (;;) {
	if (Test-Path -Path "D:\INFO_UF2.TXT" ) {
		Copy-Item -Path "C:\Users\kayfox\Documents\Badge 2025\Build7.uf2" -Destination "D:\"
	}
}