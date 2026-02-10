package com.diy.sys.entity.sign;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableLogic;
import com.baomidou.mybatisplus.annotation.TableName;
import io.swagger.v3.oas.annotations.media.Schema;
import lombok.Data;
import lombok.EqualsAndHashCode;
import lombok.experimental.Accessors;

import java.io.Serializable;
import java.time.LocalDateTime;

/**
 * <p>
 * 手语翻译历史记录表
 * </p>
 *
 * @author youzi
 * @since 2024
 */
@Data
@EqualsAndHashCode(callSuper = false)
@Accessors(chain = true)
@TableName("x_translation_history")
@Schema(name = "TranslationHistory", description = "手语翻译历史记录")
public class TranslationHistory implements Serializable {

    private static final long serialVersionUID = 1L;

    @Schema(description = "主键ID")
    @TableId(value = "id", type = IdType.AUTO)
    private Long id;

    @Schema(description = "用户ID")
    private Long userId;

    @Schema(description = "原始识别词序(JSON格式或逗号分隔)")
    private String originalWords;

    @Schema(description = "最终生成的句子")
    private String resultSentence;

    @Schema(description = "是否经过AI润色(0=否, 1=是)")
    private Integer isAiPolished;

    @Schema(description = "创建时间/练习时间")
    private LocalDateTime createTime;

    @Schema(description = "逻辑删除(0=未删, 1=已删)")
    @TableLogic
    private Integer isDeleted;
}
