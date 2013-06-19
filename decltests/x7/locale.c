/* features */
#include <locale.h>

int xx[] = {
  LC_COLLATE_MASK,
  LC_CTYPE_MASK,
  LC_MESSAGES_MASK,
  LC_MONETARY_MASK,
  LC_NUMERIC_MASK,
  LC_TIME_MASK,
  LC_ALL_MASK,
};

void ff(void)
{
  locale_t a = LC_GLOBAL_LOCALE;
  locale_t (*b)(locale_t) = duplocale;
  void     (*c)(locale_t) = freelocale;
  locale_t (*d)(int, const char *, locale_t) = newlocale;
  locale_t (*e)(locale_t) = uselocale;
}
