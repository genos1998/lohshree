/* BRAND PALETTE — the one definition of the company's colours, loaded by
   every page immediately after the Tailwind CDN so that brand-, ink- and
   blue-* class names mean the same thing everywhere.

   Kept as a plain script rather than a module: it has to run before the
   page body is parsed, and it must work when a file is opened straight
   off the disk, where modules are refused. */
tailwind.config = {
    theme: {
        extend: {
            colors: {
                brand:      '#1B2ACF',
                brandDark:  '#141FA3',
                brandLight: '#EEF1FE',
                ink:        '#111827',
                // Metallic cobalt-blue scale replacing Tailwind's blue,
                // so every blue-* tint stays on-brand
                blue: {
                    50:  '#EEF1FE',
                    100: '#DEE4FD',
                    200: '#BFCAFB',
                    300: '#95A6F6',
                    400: '#6379EE',
                    500: '#3A50E5',
                    600: '#2338DC',
                    700: '#1B2ACF',
                    800: '#141FA3',
                    900: '#0E1670',
                    950: '#081048',
                }
            }
        }
    }
}
