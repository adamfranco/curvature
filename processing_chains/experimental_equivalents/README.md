
All of the processing chains in this directory are different ways of taking
the same processing steps. All of them take a *collected* MessagePack stream that
has been generated with `bin/curvature-collect`. These chains are being used to
help us test several different methods for data streaming so that we can settle
on APIs that are both easy to understand and write and also performant on large
data-sets.

Setup
-----

First, generate your initial MessagePack data from a `.osm.pbf` file.

    bin/curvature-collect -v ~/Downloads/vermont.osm.pbf > vermont.msgpack

Calling these chains:
---------------------
Once the data has been collected each of the chains can be called by piping the
msgpack stream to its STDIN.

    cat vermont.msgpack | msgpack_pp_example.sh | ../../bin/msgpack-reader | head -n 100

    cat vermont.msgpack | reduce_chain_example.py | ../../bin/msgpack-reader | head -n 100

    cat vermont.msgpack | callback_chain_example.py | ../../bin/msgpack-reader | head -n 100
