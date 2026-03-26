# 🎨 FRONTEND REFACTOR - Guía de Implementación

## 📁 Estructura del Directorio `/frontend_refactor`

```
frontend_refactor/
├── components/           # Componentes reutilizables
│   ├── layout_refactored.html    # Layout principal accesible
│   ├── nav_refactored.html       # Navegación mejorada
│   ├── footer_refactored.html    # Footer accesible
│   └── card.html                 # Card component con skeleton
├── styles/               # Hojas de estilo
│   └── main.css                  # CSS global refactorizado
└── utils/                # Utilidades
    └── optimize_images.sh        # Script de optimización de imágenes
```

---

## 🚀 Pasos para Implementar las Mejoras

### Paso 1: Backup de Archivos Originales

```bash
cd /workspace

# Crear backup
cp portfolio/templates/layout.html portfolio/templates/layout.html.backup
cp portfolio/templates/partials/nav.html portfolio/templates/partials/nav.html.backup
cp portfolio/templates/partials/footer.html portfolio/templates/partials/footer.html.backup
cp portfolio/static/main.css portfolio/static/main.css.backup
```

### Paso 2: Copiar Componentes Refactorizados

```bash
# Copiar layout principal
cp frontend_refactor/components/layout_refactored.html portfolio/templates/layout.html

# Copiar navegación
cp frontend_refactor/components/nav_refactored.html portfolio/templates/partials/nav.html

# Copiar footer
cp frontend_refactor/components/footer_refactored.html portfolio/templates/partials/footer.html

# Copiar estilos globales
cp frontend_refactor/styles/main.css portfolio/static/main.css
```

### Paso 3: Optimizar Imágenes

```bash
# Instalar dependencias (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y imagemagick libwebp-tools optipng

# Ejecutar script de optimización
cd /workspace
./frontend_refactor/utils/optimize_images.sh \
    /workspace/portfolio/static/portfolio \
    /workspace/media/optimized \
    80
```

### Paso 4: Actualizar Template home.html

Reemplazar el bloque de proyectos en `home.html`:

**ANTES:**
```django
{% for project in projects %}
<div class="col-md-4 mb-4">
    <div class="card">
        <img src="{{ project.image.url }}" class="card-img-top" alt="{{ project.title }}">
        <div class="card-body">
            <h5 class="card-title">{{ project.title }}</h5>
            <p class="card-text">{{ project.description }}</p>
            <a href="{{ project.url }}" class="btn btn-primary">Ver más</a>
        </div>
    </div>
</div>
{% endfor %}
```

**DESPUÉS:**
```django
{% for project in projects %}
<div class="col-md-4 mb-4">
    {% include 'components/card.html' with 
        title=project.title
        content=project.description
        image_url=project.image.url
        alt_text=project.title
        button_text="Ver más"
        button_url=project.url
        metadata.author=project.author.username
        metadata.date=project.created_at
    %}
</div>
{% empty %}
<div class="col-md-12">
    <p>No se encontraron proyectos.</p>
</div>
{% endfor %}
```

### Paso 5: Configurar Django para Servir WebP

Añadir a `settings.py`:

```python
# Soporte para WebP
MIME_TYPES = {
    '.webp': 'image/webp',
}

# Añadir al final
import mimetypes
mimetypes.add_type('image/webp', '.webp')
```

### Paso 6: Verificar Cambios

```bash
# Correr tests de frontend (si existen)
python manage.py test

# Levantar servidor de desarrollo
python manage.py runserver

# Abrir en navegador y verificar:
# 1. Skip link funciona (Tab al cargar página)
# 2. Focus indicators son visibles
# 3. Imágenes cargan con lazy loading
# 4. Animaciones respetan prefers-reduced-motion
```

---

## ✅ Checklist de Verificación WCAG 2.1 AA

### Perceptible
- [ ] Textos alternativos descriptivos en todas las imágenes
- [ ] Contraste de color mínimo 4.5:1 verificado
- [ ] Contenido presentable en diferentes orientaciones
- [ ] Tamaño de texto escalable hasta 200%

### Operable
- [ ] Toda funcionalidad accesible por teclado
- [ ] Skip link funcional
- [ ] Focus visible en todos los elementos interactivos
- [ ] No hay trampas de foco
- [ ] Tiempo suficiente para leer contenido

### Comprensible
- [ ] Idioma de la página declarado (`lang="es"`)
- [ ] Navegación consistente en todas las páginas
- [ ] Labels descriptivos en formularios
- [ ] Mensajes de error claros y constructivos

### Robusto
- [ ] HTML válido y semántico
- [ ] ARIA roles usados correctamente
- [ ] Compatible con tecnologías asistivas
- [ ] Degradación elegante si JS falla

---

## 📊 Métricas de Rendimiento Esperadas

| Métrica | Antes | Después | Objetivo |
|---------|-------|---------|----------|
| LCP (Largest Contentful Paint) | ~3.2s | ~1.8s | <2.5s ✅ |
| CLS (Cumulative Layout Shift) | ~0.15 | ~0.05 | <0.1 ✅ |
| FID (First Input Delay) | ~150ms | ~50ms | <100ms ✅ |
| TTI (Time to Interactive) | ~4.5s | ~2.2s | <3.8s ✅ |
| Tamaño total de página | ~3.5MB | ~800KB | <1MB ✅ |

---

## 🛠️ Herramientas Recomendadas para Testing

### Accesibilidad
```bash
# Instalar axe-core CLI
npm install -g @axe-core/cli

# Escanear página
axe http://localhost:8000/

# Instalar pa11y
npm install -g pa11y

# Ejecutar tests
pa11y http://localhost:8000/ --standard WCAG2AA
```

### Rendimiento
```bash
# Usar Lighthouse CLI
npm install -g lighthouse

# Ejecutar auditoría
lighthouse http://localhost:8000/ --output html --output-path=./lighthouse-report.html

# O usar WebPageTest
# https://www.webpagetest.org/
```

### Validación HTML
```bash
# Usar vnu-jar
java -jar vnu.jar portfolio/templates/*.html
```

---

## 🎯 Sistema de Diseño (Design Tokens)

Los siguientes design tokens están disponibles en `main.css`:

### Colores
```css
--color-primary: #0d6efd
--color-secondary: #6c757d
--color-success: #198754
--color-warning: #ffc107
--color-danger: #dc3545
```

### Espaciado (sistema de 4px)
```css
--spacing-1: 0.25rem;  /* 4px */
--spacing-2: 0.5rem;   /* 8px */
--spacing-3: 0.75rem;  /* 12px */
--spacing-4: 1rem;     /* 16px */
--spacing-6: 1.5rem;   /* 24px */
--spacing-8: 2rem;     /* 32px */
```

### Tipografía
```css
--font-size-sm: 0.875rem;
--font-size-base: 1rem;
--font-size-lg: 1.125rem;
--font-size-xl: 1.25rem;
--font-size-2xl: 1.5rem;
```

### Sombras
```css
--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
```

---

## 🔧 Troubleshooting

### Problema: Skip link no es visible
**Solución:** Verificar que el CSS se está cargando correctamente y que no hay reglas `overflow: hidden` en el body.

### Problema: Focus indicators no se muestran
**Solución:** Algunos navegadores tienen configuraciones nativas. Probar en Chrome/Firefox latest.

### Problema: Imágenes WebP no cargan
**Solución:** Verificar MIME types en settings.py y que el servidor web esté configurado para servir WebP.

### Problema: Animaciones no se desactivan con prefers-reduced-motion
**Solución:** Verificar que la media query está correctamente implementada en todos los componentes.

---

## 📚 Recursos Adicionales

- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- [A11y Project Checklist](https://www.a11yproject.com/checklist/)
- [Web.dev Performance](https://web.dev/performance/)
- [CSS-Tricks Complete Guide to Grid](https://css-tricks.com/snippets/css/complete-guide-grid/)

---

*Guía creada como parte de la auditoría UX/UI. Para preguntas o soporte, revisar UX_UI_AUDIT.md*
