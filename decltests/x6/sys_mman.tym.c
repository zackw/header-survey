/* support for typed memory objects */
#include <sys/mman.h>

int cc[] = {
  POSIX_TYPED_MEM_ALLOCATE,
  POSIX_TYPED_MEM_ALLOCATE_CONTIG,
  POSIX_TYPED_MEM_MAP_ALLOCATABLE,
};

void f(void)
{
  struct posix_typed_mem_info tmi;
  size_t *tmil = &tmi.posix_tmi_length;

  int (*a)(const void *, size_t, off_t *, size_t *, int *)
    = posix_mem_offset;
  int (*b)(int, struct posix_typed_mem_info *) = posix_typed_mem_get_info;
  int (*c)(const char *, int, int) = posix_typed_mem_open;
}
