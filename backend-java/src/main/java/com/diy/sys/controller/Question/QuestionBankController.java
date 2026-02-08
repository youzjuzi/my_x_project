package com.diy.sys.controller.Question;


import com.diy.common.utils.PinyinUtil;
import com.diy.common.vo.Result;
import com.diy.sys.entity.Question.QuestionBank;
import com.diy.sys.service.Question.IQuestionBankService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

/**
 * <p>
 * 题目控制器
 * </p>
 *
 * @author youzi
 * @since 2024
 */

@Tag(name = "题库管理接口")
@RestController
@RequestMapping("/questionBank")
@PreAuthorize("hasPermission('/sys/question_set', 'MENU')")
public class QuestionBankController {
    @Autowired
    private IQuestionBankService questionBankService;

    /**
     * 新增题目
     *
     * @param question 题目信息
     * @return 操作结果
     */
    @Operation(summary = "新增题目")
    @PostMapping
    public Result<QuestionBank> addQuestion(@RequestBody QuestionBank question) {
        try {
            // 如果是中文类型（type = 2），自动生成拼音
            if (question.getType() == 2 && question.getContent() != null && !question.getContent().trim().isEmpty()) {
                String pinyin = PinyinUtil.toPinyin(question.getContent());
                question.setPinyin(pinyin);
            }

            // 设置默认状态为启用（如果未设置）
            if (question.getStatus() == 0) {
                question.setStatus(1);
            }

            // 如果 levelGroup 是数字，转换为字符串（根据实体类定义）
            if (question.getLevelGroup() == null) {
                question.setLevelGroup("1");
            }

            boolean success = questionBankService.save(question);
            if (success) {
                return Result.success(question, "新增题目成功");
            } else {
                return Result.fail("新增题目失败");
            }
        } catch (Exception e) {
            e.printStackTrace();
            return Result.fail("新增题目失败：" + e.getMessage());
        }
    }

    /**
     * 修改题目
     *
     * @param question 题目信息
     * @return 操作结果
     */
    @Operation(summary = "修改题目")
    @PutMapping
    public Result<?> updateQuestion(@RequestBody QuestionBank question) {
        try {
            // 如果是中文类型（type = 2），且拼音为空或需要重新生成，自动生成拼音
            if (question.getType() == 2 && question.getContent() != null) {
                // 如果拼音为空，或者内容已改变，重新生成拼音
                if (question.getPinyin() == null || question.getPinyin().isEmpty()) {
                    String pinyin = PinyinUtil.toPinyin(question.getContent());
                    question.setPinyin(pinyin);
                }
            }

            boolean success = questionBankService.updateById(question);
            if (success) {
                return Result.success(question, "修改题目成功");
            } else {
                return Result.fail("修改题目失败");
            }
        } catch (Exception e) {
            return Result.fail("修改题目失败：" + e.getMessage());
        }
    }

    /**
     * 分页查询题目列表
     *
     * @param content 题目内容（模糊查询，可选）
     * @param type 题目类型（1:单词 2:中文 3:数字，可选）
     * @param difficulty 难度（1:简单 2:中等 3:困难，可选）
     * @param levelGroup 级别组（可选）
     * @param pageNo 页码
     * @param pageSize 每页大小
     * @return 分页结果
     */
    @Operation(summary = "分页查询题目列表")
    @GetMapping("/list")
    public Result<Map<String, Object>> getQuestionList(
            @RequestParam(value = "content", required = false) String content,
            @RequestParam(value = "type", required = false) Integer type,
            @RequestParam(value = "difficulty", required = false) Integer difficulty,
            @RequestParam(value = "levelGroup", required = false) String levelGroup,
            @RequestParam("pageNo") Long pageNo,
            @RequestParam("pageSize") Long pageSize) {
        try {
            Map<String, Object> data = questionBankService.getQuestionList(content, type, difficulty, levelGroup, pageNo, pageSize);
            return Result.success(data, "查询成功");
        } catch (Exception e) {
            e.printStackTrace();
            return Result.fail("查询失败：" + e.getMessage());
        }
    }

    /**
     * 根据ID查询单个题目
     *
     * @param id 题目ID
     * @return 题目信息
     */
    @Operation(summary = "根据ID查询题目")
    @GetMapping("/{id}")
    public Result<QuestionBank> getQuestionById(@PathVariable("id") Integer id) {
        try {
            QuestionBank question = questionBankService.getById(id);
            if (question != null) {
                return Result.success(question, "查询成功");
            } else {
                return Result.fail("题目不存在");
            }
        } catch (Exception e) {
            e.printStackTrace();
            return Result.fail("查询失败：" + e.getMessage());
        }
    }

    /**
     * 根据ID删除题目
     *
     * @param id 题目ID
     * @return 操作结果
     */
    @Operation(summary = "删除题目")
    @DeleteMapping("/{id}")
    public Result<?> deleteQuestionById(@PathVariable("id") Integer id) {
        try {
            boolean success = questionBankService.removeById(id);
            if (success) {
                return Result.success("删除题目成功");
            } else {
                return Result.fail("删除题目失败，题目可能不存在");
            }
        } catch (Exception e) {
            e.printStackTrace();
            return Result.fail("删除题目失败：" + e.getMessage());
        }
    }
}
