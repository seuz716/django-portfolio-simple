#!/bin/bash

# =============================================================================
# Script de Optimización de Imágenes para Portfolio
# =============================================================================
# Este script convierte imágenes PNG/JPG a WebP optimizado y genera múltiples
# tamaños para responsive images.
#
# Requisitos:
#   - ImageMagick (convert)
#   - cwebp (Google WebP tools)
#   - optipng (opcional, para optimización adicional)
#
# Uso:
#   ./optimize_images.sh [directorio_origen] [directorio_destino]
#
# Ejemplo:
#   ./optimize_images.sh /workspace/portfolio/static/portfolio /workspace/media/optimized
# =============================================================================

set -euo pipefail

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuración por defecto
SOURCE_DIR="${1:-/workspace/portfolio/static/portfolio}"
DEST_DIR="${2:-/workspace/media/optimized}"
QUALITY="${3:-80}"

# Tamaños para responsive images (en píxeles)
SIZES=(400 800 1200 1600)

# Función para mostrar mensajes
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[OK]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar dependencias
check_dependencies() {
    log_info "Verificando dependencias..."
    
    local missing_deps=()
    
    if ! command -v convert &> /dev/null; then
        missing_deps+=("ImageMagick (convert)")
    fi
    
    if ! command -v cwebp &> /dev/null; then
        missing_deps+=("cwebp (libwebp-tools)")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        log_error "Faltan dependencias: ${missing_deps[*]}"
        echo ""
        echo "Instalar en Ubuntu/Debian:"
        echo "  sudo apt-get install imagemagick libwebp-tools optipng"
        echo ""
        echo "Instalar en macOS:"
        echo "  brew install imagemagick webp optipng"
        exit 1
    fi
    
    log_success "Todas las dependencias están instaladas"
}

# Crear directorio de destino
setup_directories() {
    log_info "Configurando directorios..."
    
    if [ ! -d "$SOURCE_DIR" ]; then
        log_error "El directorio de origen no existe: $SOURCE_DIR"
        exit 1
    fi
    
    mkdir -p "$DEST_DIR"
    mkdir -p "$DEST_DIR/thumbnails"
    mkdir -p "$DEST_DIR/medium"
    mkdir -p "$DEST_DIR/large"
    
    log_success "Directorios creados en $DEST_DIR"
}

# Optimizar una imagen individual
optimize_image() {
    local input_file="$1"
    local filename=$(basename "$input_file")
    local name="${filename%.*}"
    local extension="${filename##*.}"
    
    log_info "Procesando: $filename"
    
    # Convertir a WebP para cada tamaño
    for size in "${SIZES[@]}"; do
        local output_file=""
        local quality_adjust=$QUALITY
        
        if [ $size -le 400 ]; then
            output_file="$DEST_DIR/thumbnails/${name}-${size}w.webp"
            quality_adjust=$((QUALITY - 5))
        elif [ $size -le 800 ]; then
            output_file="$DEST_DIR/medium/${name}-${size}w.webp"
        else
            output_file="$DEST_DIR/large/${name}-${size}w.webp"
            quality_adjust=$((QUALITY + 5))
        fi
        
        # Limitar calidad entre 60-90
        quality_adjust=$((quality_adjust < 60 ? 60 : quality_adjust))
        quality_adjust=$((quality_adjust > 90 ? 90 : quality_adjust))
        
        # Redimensionar y convertir a WebP
        convert "$input_file" \
            -resize "${size}x${size}>" \
            -quality "$quality_adjust" \
            tmp_resized.png
        
        cwebp -q "$quality_adjust" \
            -metadata all \
            tmp_resized.png \
            -o "$output_file" 2>/dev/null || true
        
        rm -f tmp_resized.png
        
        if [ -f "$output_file" ]; then
            local original_size=$(stat -f%z "$input_file" 2>/dev/null || stat -c%s "$input_file")
            local optimized_size=$(stat -f%z "$output_file" 2>/dev/null || stat -c%s "$output_file")
            local savings=$(( (original_size - optimized_size) * 100 / original_size ))
            
            log_success "  → ${size}w: $(numfmt --to=iec-i --suffix=B "$optimized_size") (${savings}% menor)"
        fi
    done
    
    # Crear versión original optimizada en WebP
    local original_webp="$DEST_DIR/${name}.webp"
    cwebp -q "$QUALITY" \
        -metadata all \
        "$input_file" \
        -o "$original_webp" 2>/dev/null || true
    
    if [ -f "$original_webp" ]; then
        local original_size=$(stat -f%z "$input_file" 2>/dev/null || stat -c%s "$input_file")
        local optimized_size=$(stat -f%z "$original_webp")
        local savings=$(( (original_size - optimized_size) * 100 / original_size ))
        
        log_success "  → Original WebP: $(numfmt --to=iec-i --suffix=B "$optimized_size") (${savings}% menor)"
    fi
}

# Generar placeholder blurhado
generate_placeholder() {
    local input_file="$1"
    local filename=$(basename "$input_file")
    local name="${filename%.*}"
    
    log_info "Generando placeholder para: $filename"
    
    local placeholder="$DEST_DIR/${name}-placeholder.webp"
    
    # Crear thumbnail muy pequeño y difuminado
    convert "$input_file" \
        -resize 20x20! \
        -blur 0x3 \
        -quality 50 \
        tmp_placeholder.png
    
    cwebp -q 50 tmp_placeholder.png -o "$placeholder" 2>/dev/null || true
    rm -f tmp_placeholder.png
    
    if [ -f "$placeholder" ]; then
        log_success "  → Placeholder generado"
    fi
}

# Generar HTML snippet para responsive images
generate_html_snippet() {
    local name="$1"
    local alt_text="$2"
    
    cat << EOF
<!-- Snippet HTML para: $name -->
<picture>
  <source type="image/webp" srcset="
    {% static 'optimized/thumbnails/${name}-400w.webp' %} 400w,
    {% static 'optimized/medium/${name}-800w.webp' %} 800w,
    {% static 'optimized/large/${name}-1200w.webp' %} 1200w,
    {% static 'optimized/large/${name}-1600w.webp' %} 1600w
  " sizes="(max-width: 768px) 400px, (max-width: 1024px) 800px, 1200px">
  
  <img
    src="{% static 'optimized/${name}.webp' %}"
    alt="$alt_text"
    loading="lazy"
    decoding="async"
    width="800"
    height="600"
  >
</picture>
EOF
}

# Procesar todas las imágenes
process_all_images() {
    log_info "Buscando imágenes en $SOURCE_DIR..."
    
    local image_count=0
    local processed_count=0
    
    # Contar imágenes
    image_count=$(find "$SOURCE_DIR" -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" \) | wc -l)
    
    if [ "$image_count" -eq 0 ]; then
        log_warning "No se encontraron imágenes para procesar"
        return
    fi
    
    log_info "Encontradas $image_count imágenes"
    echo ""
    
    # Procesar cada imagen
    while IFS= read -r -d '' image; do
        optimize_image "$image"
        generate_placeholder "$image"
        ((processed_count++))
        echo ""
    done < <(find "$SOURCE_DIR" -type f \( -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.png" \) -print0)
    
    log_success "Procesadas $processed_count de $image_count imágenes"
}

# Mostrar resumen
show_summary() {
    echo ""
    echo "================================================================="
    log_success "¡Optimización completada!"
    echo "================================================================="
    echo ""
    echo "Archivos generados en: $DEST_DIR"
    echo ""
    
    # Calcular ahorro total
    local original_total=0
    local optimized_total=0
    
    if [ -d "$SOURCE_DIR" ] && [ -d "$DEST_DIR" ]; then
        original_total=$(du -sb "$SOURCE_DIR" 2>/dev/null | cut -f1 || echo 0)
        optimized_total=$(du -sb "$DEST_DIR" 2>/dev/null | cut -f1 || echo 0)
    fi
    
    if [ "$original_total" -gt 0 ] && [ "$optimized_total" -gt 0 ]; then
        local savings=$(( (original_total - optimized_total) * 100 / original_total ))
        echo "Tamaño original: $(numfmt --to=iec-i --suffix=B "$original_total")"
        echo "Tamaño optimizado: $(numfmt --to=iec-i --suffix=B "$optimized_total")"
        echo "Ahorro estimado: ${savings}%"
    fi
    
    echo ""
    echo "Siguientes pasos:"
    echo "  1. Mover archivos optimizados a tu proyecto Django"
    echo "  2. Actualizar templates para usar responsive images"
    echo "  3. Configurar Django para servir archivos WebP"
    echo ""
}

# Main
main() {
    echo ""
    echo "================================================================="
    echo "  Optimizador de Imágenes para Portfolio"
    echo "================================================================="
    echo ""
    
    check_dependencies
    setup_directories
    process_all_images
    show_summary
}

# Ejecutar main
main "$@"
