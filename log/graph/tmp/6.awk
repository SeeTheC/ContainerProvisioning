{
	subj[$0]=(subj[$0]==""?1:subj[$0]+1)
	#delete arrayname[index];
}
END{

	PROCINFO["sorted_in"]="@ind_str_asc" 
	for(k in subj)
	{
		print(k" "subj[k])
	}
}
