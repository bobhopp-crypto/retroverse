on «event facofget» this_folder given «class flst»:added_items
	repeat with anItem in added_items
		try
			set itemPath to POSIX path of anItem
			«event sysoexec» "$HOME/Sites/retroverse/tools/faststart_mp4.sh " & quoted form of itemPath
		end try
	end repeat
end «event facofget»
