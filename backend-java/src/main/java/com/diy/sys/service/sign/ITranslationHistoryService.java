package com.diy.sys.service.sign;

import com.diy.sys.entity.sign.TranslationHistory;
import com.baomidou.mybatisplus.extension.service.IService;

/**
 * <p>
 * 手语翻译历史记录表 服务类
 * </p>
 *
 * @author youzi
 * @since 2024
 */
public interface ITranslationHistoryService extends IService<TranslationHistory> {

    void saveTranslationAsync(Integer userId, String content);
}
