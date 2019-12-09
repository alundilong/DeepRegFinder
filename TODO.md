### Preprocessing
- reduce file size by using gzipped bed and saf. NOT DO
- add #threads for featureCounts. DONE
- parallelize build_histone_tensors. USED MERGE INSTEAD. DONE
- change "enhancer_slopped" to "more_slopped". NOT DO
- use "__all__" to define what to import. DONE
- modify "process_genome" DONE
- require TSS and enhancer to overlap with DHS. DONE
- sample background using a fixed number instead of ratio. DONE
- support for 3-way classification without using GRO-seq.

### Training
- add weight initialization.
- add tensorboard for training monitor. DONE