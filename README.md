=======
nekhbet
=======

Performance and profiling WSGI middleware agent and server


# License

BSD

# Introduction

WSGI filter to track request response time per URL
Expect to add some profiling too

Not to be used on production or on short time profiling only

# Requirements

Mongodb for storage

# Status

In development, not to be used for the moment

# Usage

In application .ini file (Paste like)

[app:main]
use = egg:myapp
filter-with = nekhbet

[filter:globalperf]
use = egg:nekhbet#perf_filter_factory

