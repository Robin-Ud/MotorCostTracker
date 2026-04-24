#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_DIR="$(mktemp -d /tmp/motoregis_test.XXXXXX)"

cp "$SCRIPT_DIR/motoregis.py" "$TEST_DIR/"
cp "$SCRIPT_DIR/configs.json" "$TEST_DIR/"
cp -r "$SCRIPT_DIR/veiculos" "$TEST_DIR/"

echo "🧪 Teste — dados reais não serão modificados"
echo "   ($TEST_DIR)"
echo ""

python "$TEST_DIR/motoregis.py"

echo ""
echo "--- Diferenças geradas no teste ---"
for csv in "$TEST_DIR/veiculos/"*.csv; do
    name=$(basename "$csv")
    real="$SCRIPT_DIR/veiculos/$name"
    added=$(diff "$real" "$csv" | grep "^>" | sed 's/^> /  /')
    if [ -n "$added" ]; then
        echo "  $name:"
        echo "$added"
    fi
done

echo ""
read -p "Manter arquivos em $TEST_DIR? [s/N] " keep
if [[ "$keep" == "s" || "$keep" == "S" ]]; then
    echo "📁 Mantido."
else
    rm -rf "$TEST_DIR"
    echo "🗑️  Limpo."
fi
