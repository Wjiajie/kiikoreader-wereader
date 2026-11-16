#!/usr/bin/env python3
"""S31 直连 GPIO / TPS 上电与驱动释放回归（无 Pico IOE/SY7636A）。
English: S31 direct GPIO / TPS power and drive-release regression (no Pico IOE/SY7636A).
SPDX-License-Identifier: Apache-2.0
"""
from pathlib import Path
import re
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
source = (root / 'components/read_pico/read_pico_board.c').read_text()


def function(name: str) -> str:
    m = re.search(r'^(?:static )?[^\n]+\b' + name + r'\([^;{}]*\)\s*\{', source, re.M)
    assert m, name
    at, depth = m.end(), 1
    while depth:
        if source[at] == '{':
            depth += 1
        elif source[at] == '}':
            depth -= 1
        at += 1
    return source[m.start():at]


unit = r'''
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
typedef int esp_err_t;
#define ESP_OK 0
#define ESP_FAIL -1
#define ESP_ERR_INVALID_ARG -2
#define ESP_ERROR_CHECK(x) do{esp_err_t _e=(x);assert(_e==ESP_OK);}while(0)
#define GPIO_MODE_OUTPUT 1
typedef struct {bool ep_mode,ep_output_enable,ep_stv;} epd_ctrl_state_t;
static epd_ctrl_state_t s_state;
static epd_ctrl_state_t *epd_ctrl_state(void){return &s_state;}
static int gpio_levels[64];
static unsigned gpio_writes,tps_on_calls,tps_off_calls;
static bool tps_ready=true,tps_on_fail;
static int vcom=3000;
static esp_err_t gpio_set_level(int pin,int level){assert(pin>=0&&pin<64);++gpio_writes;gpio_levels[pin]=level;return ESP_OK;}
static esp_err_t gpio_set_direction(int pin,int mode){(void)pin;(void)mode;return ESP_OK;}
static esp_err_t gpio_hold_dis(int pin){(void)pin;return ESP_OK;}
static int gpio_get_level(int pin){return gpio_levels[pin];}
static bool metalio_tps_ready(void){return tps_ready;}
static esp_err_t metalio_tps_on(int vcom){(void)vcom;++tps_on_calls;return tps_on_fail?ESP_FAIL:ESP_OK;}
static void metalio_tps_off(void){++tps_off_calls;tps_ready=false;}
'''
for name in ['board_set_ctrl', 'board_on', 'board_off', 'read_pico_epd_release_drive']:
    unit += function(name) + '\n'
unit += r'''
int main(void){
 epd_ctrl_state_t state={0};
 epd_ctrl_state_t mode={.ep_mode=true},output={.ep_output_enable=true},stv={.ep_stv=true};
 // TPS 未就绪时 MODE/XOE 不得抬高。/ MODE/XOE stay low until TPS is ready.
 tps_ready=false;state.ep_mode=true;board_set_ctrl(&state,&mode);assert(gpio_levels[19]==0);
 state.ep_output_enable=true;board_set_ctrl(&state,&output);assert(gpio_levels[18]==0);
 tps_ready=true;board_set_ctrl(&state,&mode);assert(gpio_levels[19]==1);
 board_set_ctrl(&state,&output);assert(gpio_levels[18]==1);
 state.ep_stv=true;board_set_ctrl(&state,&stv);assert(gpio_levels[35]==1);
 // 上电失败不得留下可驱动的 MODE/XOE。/ A failed rail bring-up must not leave MODE/XOE driven.
 tps_on_fail=true;tps_on_calls=0;board_on(&state);
 assert(tps_on_calls==1&&!state.ep_mode&&!state.ep_output_enable&&gpio_levels[18]==0&&gpio_levels[19]==0);
 tps_on_fail=false;tps_ready=true;board_on(&state);assert(tps_on_calls==2);
 // 公共完成出口必须拉低驱动脚，且不影响其他 GPIO 影子。/ Common completion must drop drive pins without touching unrelated GPIO shadows.
 gpio_levels[8]=1;unsigned before=gpio_writes;
 assert(read_pico_epd_release_drive());
 assert(!state.ep_mode&&!state.ep_output_enable&&gpio_levels[18]==0&&gpio_levels[19]==0&&gpio_levels[8]==1);
 assert(gpio_writes==before+2);
 for(int i=0;i<100;++i)assert(read_pico_epd_release_drive());
 board_off(&state);assert(tps_off_calls==1&&!state.ep_stv&&gpio_levels[35]==0);
 puts("PASS: S31 TPS-gated MODE/XOE, failed bring-up, drive release and power-off");
}
'''
with tempfile.TemporaryDirectory(prefix='pmic-gate-') as temporary:
    work = Path(temporary)
    (work / 'metalio_hw.h').write_text('#pragma once\n#include <stdbool.h>\n#include <stdint.h>\ntypedef int esp_err_t;\n')
    (work / 'epdiy.h').write_text('#pragma once\ntypedef struct{bool ep_mode,ep_output_enable,ep_stv;}epd_ctrl_state_t;\ntypedef struct{void*unused;}EpdBoardDefinition;\n')
    (work / 'driver').mkdir()
    (work / 'driver/gpio.h').write_text('#pragma once\n')
    (work / 'freertos').mkdir()
    (work / 'freertos/FreeRTOS.h').write_text('#pragma once\n')
    (work / 'freertos/task.h').write_text('#pragma once\n#define pdMS_TO_TICKS(n) (n)\n')
    (work / 'read_pico_board.h').write_text('#pragma once\n')
    (work / 'read_pico_epd_timing.h').write_text('#pragma once\nenum{READ_PICO_EPD_SCAN_FULL=0};\n')
    (work / 'test.c').write_text(unit)
    binary = work / 'test'
    subprocess.run(
        ['cc', '-std=c11', '-Wall', '-Wextra', '-Werror', '-Wno-unused-function',
         '-fsanitize=address,undefined', '-I' + str(work), str(work / 'test.c'), '-o', str(binary)],
        check=True,
    )
    subprocess.run([str(binary)], check=True)
