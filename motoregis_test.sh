#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_DIR="$(mktemp -d /tmp/motoregis_test.XXXXXX)"
DADOS="$SCRIPT_DIR/pessoal"
[ -d "$DADOS" ] || DADOS="$SCRIPT_DIR/exemplo"

cp "$SCRIPT_DIR/motoregis.py" "$TEST_DIR/"
mkdir "$TEST_DIR/pessoal"
cp "$DADOS/configs.json" "$TEST_DIR/pessoal/"
cp -r "$DADOS/veiculos" "$TEST_DIR/pessoal/"

echo "🧪 Teste — dados reais não serão modificados"
echo "   ($TEST_DIR)"
echo ""

python "$TEST_DIR/motoregis.py"

echo ""
echo "--- Diferenças geradas no teste ---"
for csv in "$TEST_DIR/pessoal/veiculos/"*.csv; do
    name=$(basename "$csv")
    real="$DADOS/veiculos/$name"
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
