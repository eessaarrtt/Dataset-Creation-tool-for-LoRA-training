"""Модуль для автоматического обновления скрипта через git"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Tuple

try:
    from i18n import get_i18n
    I18N_AVAILABLE = True
except ImportError:
    I18N_AVAILABLE = False
    def get_i18n():
        class SimpleI18n:
            def t(self, key, **kwargs):
                return key
        return SimpleI18n()


class Updater:
    """Класс для управления обновлениями через git"""
    
    def __init__(self, repo_path: str = None):
        """
        Инициализация обновлятора
        
        Args:
            repo_path: Путь к репозиторию (по умолчанию - корень проекта)
        """
        if repo_path is None:
            # Определяем корень проекта (где находится main.py)
            repo_path = Path(__file__).parent.parent.absolute()
        self.repo_path = Path(repo_path)
        self.i18n = get_i18n()
    
    def is_git_repo(self) -> bool:
        """Проверяет, является ли директория git репозиторием"""
        git_dir = self.repo_path / '.git'
        return git_dir.exists() and git_dir.is_dir()
    
    def get_current_branch(self) -> str:
        """Получает текущую ветку git"""
        if not self.is_git_repo():
            return None
        
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None
    
    def get_current_commit(self) -> str:
        """Получает текущий коммит (короткий хеш)"""
        if not self.is_git_repo():
            return None
        
        try:
            result = subprocess.run(
                ['git', 'rev-parse', '--short', 'HEAD'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            return None
    
    def check_for_updates(self) -> Tuple[bool, str]:
        """
        Проверяет наличие обновлений в удаленном репозитории
        
        Returns:
            tuple: (есть_обновления: bool, сообщение: str)
        """
        if not self.is_git_repo():
            return False, self.i18n.t('not_git_repo')
        
        try:
            # Получаем информацию об удаленном репозитории
            result = subprocess.run(
                ['git', 'fetch', 'origin'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                return False, self.i18n.t('fetch_failed', error=result.stderr[:200])
            
            # Сравниваем локальную и удаленную версии
            current_branch = self.get_current_branch()
            if not current_branch:
                return False, self.i18n.t('cannot_determine_branch')
            
            # Проверяем, есть ли новые коммиты
            result = subprocess.run(
                ['git', 'rev-list', '--count', f'HEAD..origin/{current_branch}'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            commits_behind = int(result.stdout.strip())
            
            if commits_behind > 0:
                # Получаем информацию о новых коммитах
                result = subprocess.run(
                    ['git', 'log', f'HEAD..origin/{current_branch}', '--oneline', '-5'],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    check=True
                )
                commits_info = result.stdout.strip()
                return True, self.i18n.t('updates_available', count=commits_behind, commits=commits_info[:500])
            else:
                return False, self.i18n.t('no_updates_available')
                
        except subprocess.TimeoutExpired:
            return False, self.i18n.t('update_check_timeout')
        except subprocess.CalledProcessError as e:
            return False, self.i18n.t('update_check_failed', error=str(e)[:200])
        except FileNotFoundError:
            return False, self.i18n.t('git_not_installed')
        except Exception as e:
            return False, self.i18n.t('update_check_error', error=str(e)[:200])
    
    def update(self, force: bool = False) -> Tuple[bool, str]:
        """
        Обновляет репозиторий через git pull
        
        Args:
            force: Принудительное обновление (git reset --hard)
        
        Returns:
            tuple: (успех: bool, сообщение: str)
        """
        if not self.is_git_repo():
            return False, self.i18n.t('not_git_repo')
        
        try:
            current_commit = self.get_current_commit()
            current_branch = self.get_current_branch()
            
            print(f"   📥 {self.i18n.t('updating_repository')}...")
            print(f"   {self.i18n.t('current_version', commit=current_commit, branch=current_branch)}")
            
            # Сохраняем изменения если есть незакоммиченные файлы
            if not force:
                # Проверяем статус
                status_result = subprocess.run(
                    ['git', 'status', '--porcelain'],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                if status_result.stdout.strip():
                    # Есть незакоммиченные изменения
                    print(f"   ⚠️  {self.i18n.t('uncommitted_changes_warning')}")
                    response = input(f"   {self.i18n.t('stash_changes_prompt')} (y/n): ").strip().lower()
                    if response == 'y':
                        subprocess.run(
                            ['git', 'stash'],
                            cwd=self.repo_path,
                            check=True
                        )
                        print(f"   ✓ {self.i18n.t('changes_stashed')}")
            
            # Выполняем git pull
            if force:
                # Принудительное обновление
                subprocess.run(
                    ['git', 'fetch', 'origin'],
                    cwd=self.repo_path,
                    check=True
                )
                subprocess.run(
                    ['git', 'reset', '--hard', f'origin/{current_branch}'],
                    cwd=self.repo_path,
                    check=True
                )
            else:
                # Обычное обновление
                result = subprocess.run(
                    ['git', 'pull', 'origin', current_branch],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    check=True
                )
            
            new_commit = self.get_current_commit()
            
            if new_commit != current_commit:
                return True, self.i18n.t('update_success', old_commit=current_commit, new_commit=new_commit)
            else:
                return True, self.i18n.t('already_up_to_date')
                
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if hasattr(e, 'stderr') and e.stderr else str(e)
            return False, self.i18n.t('update_failed', error=error_msg[:300])
        except FileNotFoundError:
            return False, self.i18n.t('git_not_installed')
        except Exception as e:
            return False, self.i18n.t('update_error', error=str(e)[:300])
    
    def show_status(self):
        """Показывает текущий статус репозитория"""
        if not self.is_git_repo():
            print(f"   ⚠️  {self.i18n.t('not_git_repo')}")
            return
        
        current_commit = self.get_current_commit()
        current_branch = self.get_current_branch()
        
        if current_commit and current_branch:
            print(f"   📌 {self.i18n.t('current_version', commit=current_commit, branch=current_branch)}")
        else:
            print(f"   ⚠️  {self.i18n.t('cannot_get_version')}")

