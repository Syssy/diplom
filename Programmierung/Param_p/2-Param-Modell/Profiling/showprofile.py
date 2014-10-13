import pstats

fname = 'sim.prof'
stats = pstats.Stats(fname)
# Clean up filenames for the report
stats.strip_dirs()

stats.sort_stats('time')
stats.print_stats(20)
# Sort the statistics by the cumulative time spent in the function
stats.sort_stats('cumulative')
stats.print_stats(20) 

#stats.sort_stats('ncalls')
#stats.print_stats(20)