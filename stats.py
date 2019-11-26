import pstats
p = pstats.Stats('profile.stats')
#p.strip_dirs().sort_stats(0).print_stats() # sort by ncalls
p.strip_dirs().sort_stats(1).print_stats() # sort by tottime