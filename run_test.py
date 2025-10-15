#!/usr/bin/env python3
# run_tests.py
"""
Script para ejecutar pruebas del analizador semántico de B-Minor
"""

import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich import print

# Importar módulos del compilador
from bminor_lexer import BMinorLexer
from bminor_parser import BMinorParser
from checker import Check

console = Console()


def test_file(filename, should_pass=True):
    """
    Prueba un archivo B-Minor
    
    Args:
        filename: ruta al archivo
        should_pass: True si se espera que pase, False si debe fallar
    """
    print(f"\n{'='*70}")
    print(f"Probando: [cyan]{filename}[/cyan]")
    print(f"Expectativa: [yellow]{'✓ Debe pasar' if should_pass else '✗ Debe fallar'}[/yellow]")
    print('='*70)
    
    try:
        # Leer archivo
        with open(filename, 'r', encoding='utf-8') as f:
            text = f.read()
        
        # Análisis léxico y sintáctico
        lexer = BMinorLexer()
        parser = BMinorParser()
        
        print("\n[blue]Fase 1:[/blue] Análisis léxico y sintáctico...")
        ast = parser.parse(lexer.tokenize(text))
        
        if ast is None:
            print("[red]✗ Error en análisis sintáctico[/red]")
            return False
        
        print("[green]✓ Análisis sintáctico exitoso[/green]")
        
        # Análisis semántico
        print("\n[blue]Fase 2:[/blue] Análisis semántico...")
        symtab, errors = Check.check(ast)
        
        if errors:
            print(f"\n[red]✗ Se encontraron {len(errors)} errores semánticos:[/red]")
            for i, error in enumerate(errors, 1):
                print(f"  {i}. {error}")
            
            if should_pass:
                print("\n[red]FALLO: Se esperaba que pasara pero falló[/red]")
                return False
            else:
                print("\n[green]ÉXITO: Falló como se esperaba[/green]")
                return True
        else:
            print("\n[green]✓ Análisis semántico exitoso[/green]")
            
            # Mostrar tabla de símbolos
            print("\n[blue]Tabla de símbolos:[/blue]")
            symtab.print()
            
            if should_pass:
                print("\n[green]ÉXITO: Pasó como se esperaba[/green]")
                return True
            else:
                print("\n[red]FALLO: Se esperaba que fallara pero pasó[/red]")
                return False
                
    except FileNotFoundError:
        print(f"[red]Error: No se encontró el archivo '{filename}'[/red]")
        return False
    except Exception as e:
        print(f"[red]Error inesperado: {e}[/red]")
        import traceback
        traceback.print_exc()
        return False


def run_test_suite():
    """
    Ejecuta suite completa de pruebas
    """
    tests = [
        ("test_semantic.bminor", True),   # Debe pasar
        ("test_errors.bminor", False),     # Debe fallar
    ]
    
    results = []
    
    print("\n" + "="*70)
    print("SUITE DE PRUEBAS DEL ANALIZADOR SEMÁNTICO B-MINOR")
    print("="*70)
    
    for filename, should_pass in tests:
        if Path(filename).exists():
            result = test_file(filename, should_pass)
            results.append((filename, result))
        else:
            print(f"\n[yellow]Advertencia: Archivo '{filename}' no encontrado[/yellow]")
            results.append((filename, None))
    
    # Resumen final
    print("\n" + "="*70)
    print("RESUMEN DE PRUEBAS")
    print("="*70 + "\n")
    
    table = Table(title="Resultados")
    table.add_column("Archivo", style="cyan")
    table.add_column("Resultado", style="bold")
    
    passed = 0
    failed = 0
    skipped = 0
    
    for filename, result in results:
        if result is None:
            table.add_row(filename, "[yellow]OMITIDO[/yellow]")
            skipped += 1
        elif result:
            table.add_row(filename, "[green]✓ PASÓ[/green]")
            passed += 1
        else:
            table.add_row(filename, "[red]✗ FALLÓ[/red]")
            failed += 1
    
    console.print(table)
    
    print(f"\n[green]Pasadas:[/green] {passed}")
    print(f"[red]Fallidas:[/red] {failed}")
    print(f"[yellow]Omitidas:[/yellow] {skipped}")
    print(f"[cyan]Total:[/cyan] {len(results)}\n")
    
    return failed == 0


def test_interactive():
    """
    Modo interactivo para probar código B-Minor
    """
    print("\n" + "="*70)
    print("MODO INTERACTIVO - ANALIZADOR SEMÁNTICO B-MINOR")
    print("="*70)
    print("\nEscribe código B-Minor (escribe 'EOF' en una línea para terminar):")
    print("Ejemplo:")
    print("  x: integer = 5;")
    print("  y: integer = x + 10;")
    print("  EOF")
    print()
    
    lines = []
    while True:
        try:
            line = input(">>> ")
            if line.strip() == "EOF":
                break
            lines.append(line)
        except EOFError:
            break
    
    if not lines:
        print("[yellow]No se ingresó código[/yellow]")
        return
    
    text = "\n".join(lines)
    
    # Análisis
    lexer = BMinorLexer()
    parser = BMinorParser()
    
    print("\n[blue]Analizando...[/blue]\n")
    
    try:
        ast = parser.parse(lexer.tokenize(text))
        
        if ast is None:
            print("[red]✗ Error en análisis sintáctico[/red]")
            return
        
        print("[green]✓ Análisis sintáctico exitoso[/green]\n")
        
        symtab, errors = Check.check(ast)
        
        if errors:
            print(f"[red]✗ Errores semánticos encontrados:[/red]\n")
            for i, error in enumerate(errors, 1):
                print(f"  {i}. {error}")
        else:
            print("[green]✓ Análisis semántico exitoso[/green]\n")
            print("[blue]Tabla de símbolos:[/blue]")
            symtab.print()
            
    except Exception as e:
        print(f"[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()


def main():
    """
    Función principal
    """
    if len(sys.argv) == 1:
        # Sin argumentos: ejecutar suite de pruebas
        success = run_test_suite()
        sys.exit(0 if success else 1)
    
    elif len(sys.argv) == 2:
        if sys.argv[1] == "-i" or sys.argv[1] == "--interactive":
            # Modo interactivo
            test_interactive()
        elif sys.argv[1] == "-h" or sys.argv[1] == "--help":
            # Ayuda
            print("Uso:")
            print("  python run_tests.py                    # Ejecutar suite de pruebas")
            print("  python run_tests.py archivo.bminor     # Probar un archivo específico")
            print("  python run_tests.py -i                 # Modo interactivo")
            print("  python run_tests.py -h                 # Mostrar esta ayuda")
        else:
            # Probar archivo específico
            filename = sys.argv[1]
            result = test_file(filename, should_pass=True)
            sys.exit(0 if result else 1)
    
    else:
        print("Error: Demasiados argumentos")
        print("Usa 'python run_tests.py -h' para ayuda")
        sys.exit(1)


if __name__ == "__main__":
    main()