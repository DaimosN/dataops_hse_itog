#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Управление промптами в MLflow
"""

import argparse
from mlflow_prompts import (
    list_all_prompts,
    get_prompt_by_version,
    compare_prompt_versions,
    delete_prompt_version,
    export_prompts_to_file
)


def main():
    parser = argparse.ArgumentParser(description='Управление промптами в MLflow')
    parser.add_argument('action', choices=['list', 'get', 'compare', 'delete', 'export'],
                        help='Действие с промптами')
    parser.add_argument('--name', help='Название промпта')
    parser.add_argument('--version', help='Версия промпта')
    parser.add_argument('--output', default='prompts_export.json',
                        help='Файл для экспорта')

    args = parser.parse_args()

    if args.action == 'list':
        list_all_prompts()

    elif args.action == 'get':
        if not args.name:
            print("❌ Укажите --name")
            return
        prompt = get_prompt_by_version(args.name, args.version or "latest")
        if prompt:
            print("\n📝 Найден промпт:")
            print(json.dumps(prompt, ensure_ascii=False, indent=2))

    elif args.action == 'compare':
        if not args.name:
            print("❌ Укажите --name")
            return
        versions = args.version.split(',') if args.version else None
        compare_prompt_versions(args.name, versions)

    elif args.action == 'delete':
        if not args.name or not args.version:
            print("❌ Укажите --name и --version")
            return
        delete_prompt_version(args.name, args.version)

    elif args.action == 'export':
        export_prompts_to_file(args.output)


if __name__ == "__main__":
    main()