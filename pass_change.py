import numpy as np

from func.changer import *

path = "files/config.toml"
with open(path, "rb") as f:
    config = tomllib.load(f)

pass_on = config['info']['pass_on']
change = config['info']['change_pass']
sip_pass_on = config['info']['sip']
pass_change = Changer(
    config['info']['login'],
    config['info']['password'],
    config['info']['server'],
    config['info']['domain_name'],
    config['info']['user_list'],
    config['info']['new_password']
)


def main():
    pass_change.logging_setup_and_start()
    pass_change.server_connect()
    pass_change.server_login()

    def exit_changer():
        pass_change.server.disconnect()
        logging.info('The operations were completed successfully')
        print('The operations were completed successfully!')
        sys.exit(0)

    list_name = list((pass_change.server.list_accounts(pass_change.domain[1:])['body']).keys())
    text = f"1 - Создать файл {pass_change.users_xlsx} со всеми аккаунтами домена {pass_change.domain}\n"

    if sip_pass_on:
        text += (
            f"2 - Создать файл {pass_change.users_xlsx} со всеми аккаунтами домена "
            f"{pass_change.domain} и задать сгенерированные SIP пароли\n"
            f"3 - Сгенерировать и задать SIP пароли для аккаунтов домена {pass_change.domain} из "
            f"файла {pass_change.users_xlsx}\n"
            f"4 - Заменить/Создать SIP пароли из файла {pass_change.users_xlsx} аккаунтам домена {pass_change.domain}\n"
        )
    else:
        text += (
            f"2 - Создать файл {pass_change.users_xlsx} со всеми аккаунтами домена {pass_change.domain} и "
            f"задать пароли\n"
        )
    while True:
        option = int(input(text + "Ввод: "))
        if option in (1, 2):
            # creating a xlsx file with users
            try:
                check = os.path.exists(pass_change.path_user_xlsx)
                if check:
                    raise FileExistsError(
                        f'File already exists, all actions have been '
                        f'performed on the data in the file {pass_change.users_xlsx}'
                    )
                else:
                    pass_change.create_excel(list_name)
            except FileExistsError as e:
                logging.info(e)
            if option == 1:
                exit_changer()
            break
        elif option in (3, 4) and sip_pass_on:
            break
        else:
            print("Введено некорректное значение, попробуйте еще раз")

    # reading the xlsx file with users and changing passwords
    file_users = pd.read_excel(pass_change.path_user_xlsx, usecols=[0])
    file_sip_pass = pd.read_excel(pass_change.path_user_xlsx, usecols=[1])

    # read xlsx file with users and change passwords
    if sip_pass_on:
        for acc, password in zip(file_users.values[0], file_sip_pass.values[0]):
            pass_change.user = acc
            if option in (2, 3):
                pass_change.gen_pass()
                pass_change.set_password(1)
                pass_change.user_pass_dict['UserName'].append(pass_change.user)
                pass_change.user_pass_dict['Password'].append(pass_change.new_password)
            if option == 4:
                pass_change.new_password = str(password)
                pass_change.set_password(1)
        if option in (2, 3):
            pass_change.add_user_sip_passwords_to_excel()
        exit_changer()
    for acc in file_users.values[0]:
        pass_change.user = acc
        if pass_on == 1:
            pass_change.switch_pass_on()
        if pass_on == 0:
            pass_change.switch_pass_off()
        if change:
            if pass_change.new_password == 'none':
                pass_change.gen_pass()
                pass_change.set_password()
                pass_change.user_pass_dict['UserName'].append(pass_change.user)
                pass_change.user_pass_dict['Password'].append(pass_change.new_password)
                pass_change.new_password = 'none'
            else:
                pass_change.set_password()

    if pass_change.new_password == 'none' and change and not sip_pass_on:
        pass_change.add_users_passwords_to_excel()
    if pass_change.new_password != 'none' and not sip_pass_on:
        pass_change.delete_xlsx_sheet()

    exit_changer()


if __name__ == '__main__':
    main()
