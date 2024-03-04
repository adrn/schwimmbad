from schwimmbad.mpi import MPI

if MPI is not None:
    TEST_MPI = True
else:
    TEST_MPI = False
