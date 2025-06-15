"""
创建管理员用户的Django管理命令
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from lottery.models import UserProfile


class Command(BaseCommand):
    help = '创建管理员用户'

    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='用户名', required=True)
        parser.add_argument('--email', type=str, help='邮箱', required=True)
        parser.add_argument('--password', type=str, help='密码', required=True)
        parser.add_argument('--force', action='store_true', help='强制更新已存在的用户')

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']
        force = options['force']

        try:
            # 检查用户是否已存在
            if User.objects.filter(username=username).exists():
                if not force:
                    self.stdout.write(
                        self.style.ERROR(f'用户 {username} 已存在，使用 --force 参数强制更新')
                    )
                    return
                else:
                    # 更新现有用户
                    user = User.objects.get(username=username)
                    user.email = email
                    user.set_password(password)
                    user.is_active = True
                    user.is_staff = True
                    user.is_superuser = True
                    user.save()
                    
                    # 更新用户扩展信息
                    profile, created = UserProfile.objects.get_or_create(
                        user=user,
                        defaults={'user_type': 'admin'}
                    )
                    if not created:
                        profile.user_type = 'admin'
                        profile.save()
                    
                    self.stdout.write(
                        self.style.SUCCESS(f'管理员用户 {username} 更新成功')
                    )
            else:
                # 创建新用户
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password
                )
                
                # 设置Django超级用户权限
                user.is_staff = True
                user.is_superuser = True
                user.save()
                
                # 创建用户扩展信息
                UserProfile.objects.create(
                    user=user,
                    user_type='admin'
                )
                
                self.stdout.write(
                    self.style.SUCCESS(f'管理员用户 {username} 创建成功')
                )
            
            self.stdout.write(
                self.style.SUCCESS(f'用户详情：')
            )
            self.stdout.write(f'  用户名: {username}')
            self.stdout.write(f'  邮箱: {email}')
            self.stdout.write(f'  用户类型: 管理员')
            self.stdout.write(f'  Django权限: 超级用户')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'创建管理员用户失败: {str(e)}')
            ) 