package net.az3l1t.analysis.infrastructure.adapter.in.rest;

import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
import io.swagger.v3.oas.annotations.responses.ApiResponses;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import net.az3l1t.analysis.domain.model.AnalysisResult;
import net.az3l1t.analysis.infrastructure.adapter.in.rest.dto.in.CreateInResultDto;
import net.az3l1t.analysis.infrastructure.adapter.in.rest.dto.in.UpdateInResultDto;
import net.az3l1t.analysis.infrastructure.adapter.in.rest.dto.out.GetOutResultDto;
import net.az3l1t.analysis.infrastructure.adapter.in.rest.dto.out.UpdateOutResultDto;
import net.az3l1t.analysis.infrastructure.adapter.in.rest.mapper.ResultControllerMapper;
import net.az3l1t.analysis.infrastructure.adapter.out.artemis.dto.SendResultsDto;
import org.springframework.data.domain.Page;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;
import net.az3l1t.analysis.domain.port.in.AnalysisResultUseCase;

import java.util.Optional;

@RestController
@RequestMapping("/api/result")
@RequiredArgsConstructor
@Tag(name = "Analysis Results", description = "API для управления результатами анализов пациентов")
public class ResultController {
    private final AnalysisResultUseCase analysisResultUseCase;
    private final ResultControllerMapper resultControllerMapper;

    @PostMapping(produces = MediaType.APPLICATION_JSON_VALUE, consumes = MediaType.APPLICATION_JSON_VALUE)
    @Operation(
            summary = "Создать новый результат анализа",
            description = """
                    Создает новый результат анализа для пациента.
                    
                    **Параметры:**
                    - `patientId` - ID пациента (обязательное поле)
                    - `doctorId` - ID врача, проводившего анализ (обязательное поле)
                    - `isConfirmed` - Флаг подтверждения результата (по умолчанию false)
                    - `results` - Map с результатами анализов, где ключ - название анализа, значение - результат
                    
                    **Пример результатов:**
                    ```json
                    {
                      "hb": "12.1",
                      "rbc": "4.5",
                      "wbc": "6.8"
                    }
                    ```
                    
                    Возвращает созданный результат с присвоенным ID и временем создания.
                    """
    )
    @ApiResponses(value = {
            @ApiResponse(
                    responseCode = "200",
                    description = "Результат успешно создан",
                    content = @Content(schema = @Schema(implementation = GetOutResultDto.class))
            ),
            @ApiResponse(
                    responseCode = "400",
                    description = "Неверный запрос - отсутствуют обязательные поля",
                    content = @Content
            ),
            @ApiResponse(
                    responseCode = "401",
                    description = "Не авторизован - требуется JWT токен",
                    content = @Content
            ),
            @ApiResponse(
                    responseCode = "500",
                    description = "Внутренняя ошибка сервера",
                    content = @Content
            )
    })
    @ResponseStatus(HttpStatus.OK)
    public GetOutResultDto create(
            @io.swagger.v3.oas.annotations.parameters.RequestBody(
                    description = "Данные для создания результата анализа",
                    required = true,
                    content = @Content(schema = @Schema(implementation = CreateInResultDto.class))
            )
            @RequestBody CreateInResultDto createInResultDto) {
        return resultControllerMapper.toDtoGet(analysisResultUseCase.create(createInResultDto));
    }

    @PutMapping(produces = MediaType.APPLICATION_JSON_VALUE, consumes = MediaType.APPLICATION_JSON_VALUE)
    @Operation(
            summary = "Обновить существующий результат анализа",
            description = """
                    Обновляет существующий результат анализа.
                    
                    **Параметры:**
                    - `id` - ID результата анализа для обновления (обязательное поле)
                    - `patientId` - ID пациента (опционально)
                    - `doctorId` - ID врача (опционально)
                    - `isConfirmed` - Флаг подтверждения (опционально)
                    - `results` - Map с обновленными результатами анализов (опционально)
                    
                    Все поля кроме `id` опциональны. Обновляются только переданные поля.
                    """
    )
    @ApiResponses(value = {
            @ApiResponse(
                    responseCode = "200",
                    description = "Результат успешно обновлен",
                    content = @Content(schema = @Schema(implementation = UpdateOutResultDto.class))
            ),
            @ApiResponse(
                    responseCode = "400",
                    description = "Неверный запрос - отсутствует ID",
                    content = @Content
            ),
            @ApiResponse(
                    responseCode = "404",
                    description = "Результат анализа не найден",
                    content = @Content
            ),
            @ApiResponse(
                    responseCode = "401",
                    description = "Не авторизован",
                    content = @Content
            )
    })
    @ResponseStatus(HttpStatus.OK)
    public UpdateOutResultDto update(
            @io.swagger.v3.oas.annotations.parameters.RequestBody(
                    description = "Данные для обновления результата анализа",
                    required = true,
                    content = @Content(schema = @Schema(implementation = UpdateInResultDto.class))
            )
            @RequestBody UpdateInResultDto updateInResultDto) {
        return resultControllerMapper.toDtoUpdate(analysisResultUseCase.update(updateInResultDto));
    }

    @PutMapping(value = "/confirm/{id}", produces = MediaType.APPLICATION_JSON_VALUE)
    @Operation(
            summary = "Подтвердить результат анализа",
            description = """
                    Подтверждает результат анализа, устанавливая флаг `isConfirmed` в `true`.
                    
                    Подтвержденные результаты могут быть отправлены во внешние системы через JMS.
                    
                    **Параметры:**
                    - `id` - ID результата анализа для подтверждения
                    """
    )
    @ApiResponses(value = {
            @ApiResponse(
                    responseCode = "200",
                    description = "Результат успешно подтвержден",
                    content = @Content
            ),
            @ApiResponse(
                    responseCode = "404",
                    description = "Результат анализа не найден",
                    content = @Content
            ),
            @ApiResponse(
                    responseCode = "401",
                    description = "Не авторизован",
                    content = @Content
            )
    })
    @ResponseStatus(HttpStatus.OK)
    public void confirm(
            @Parameter(
                    description = "ID результата анализа для подтверждения",
                    required = true,
                    example = "507f1f77bcf86cd799439011"
            )
            @PathVariable String id) {
        analysisResultUseCase.confirmAnalysisResult(id);
    }

    @GetMapping(value = "/{id}", produces = MediaType.APPLICATION_JSON_VALUE)
    @Operation(
            summary = "Получить результат анализа по ID",
            description = """
                    Возвращает результат анализа по указанному ID.
                    
                    **Параметры:**
                    - `id` - ID результата анализа
                    
                    **Возвращает:**
                    - Объект `AnalysisResult` с полной информацией о результате анализа, включая:
                      - ID результата
                      - ID пациента и врача
                      - Время создания анализа
                      - Флаг подтверждения
                      - Map с результатами анализов
                    
                    Возвращает `null` если результат не найден.
                    """
    )
    @ApiResponses(value = {
            @ApiResponse(
                    responseCode = "200",
                    description = "Результат найден",
                    content = @Content(schema = @Schema(implementation = AnalysisResult.class))
            ),
            @ApiResponse(
                    responseCode = "404",
                    description = "Результат анализа не найден",
                    content = @Content
            ),
            @ApiResponse(
                    responseCode = "401",
                    description = "Не авторизован",
                    content = @Content
            )
    })
    @ResponseStatus(HttpStatus.OK)
    public Optional<AnalysisResult> getById(
            @Parameter(
                    description = "ID результата анализа",
                    required = true,
                    example = "507f1f77bcf86cd799439011"
            )
            @PathVariable String id) {
        return analysisResultUseCase.getById(id);
    }

    @GetMapping(value = "/external/{id}", produces = MediaType.APPLICATION_JSON_VALUE)
    @Operation(
            summary = "Получить подтвержденный результат из внешней системы",
            description = """
                    Получает подтвержденный результат анализа из внешней системы (EMIAS).
                    
                    Этот endpoint делает запрос к внешнему сервису для получения подтвержденного результата.
                    
                    **Параметры:**
                    - `id` - ID результата анализа во внешней системе
                    
                    **Возвращает:**
                    - Объект `SendResultsDto` с данными результата из внешней системы
                    """
    )
    @ApiResponses(value = {
            @ApiResponse(
                    responseCode = "200",
                    description = "Результат успешно получен из внешней системы",
                    content = @Content(schema = @Schema(implementation = SendResultsDto.class))
            ),
            @ApiResponse(
                    responseCode = "404",
                    description = "Результат не найден во внешней системе",
                    content = @Content
            ),
            @ApiResponse(
                    responseCode = "503",
                    description = "Внешняя система недоступна",
                    content = @Content
            ),
            @ApiResponse(
                    responseCode = "401",
                    description = "Не авторизован",
                    content = @Content
            )
    })
    @ResponseStatus(HttpStatus.OK)
    public SendResultsDto getExternalResult(
            @Parameter(
                    description = "ID результата анализа во внешней системе",
                    required = true,
                    example = "507f1f77bcf86cd799439011"
            )
            @PathVariable String id) {
        return analysisResultUseCase.getConfirmedResults(id);
    }

    @GetMapping(produces = MediaType.APPLICATION_JSON_VALUE)
    @Operation(
            summary = "Получить список результатов анализов с пагинацией",
            description = """
                    Возвращает страницу с результатами анализов с поддержкой пагинации.
                    
                    **Параметры запроса:**
                    - `page` - Номер страницы (начиная с 0, по умолчанию 0)
                    - `size` - Размер страницы (по умолчанию 10)
                    
                    **Возвращает:**
                    - Объект `Page<AnalysisResult>` со следующими полями:
                      - `content` - Список результатов на текущей странице
                      - `totalElements` - Общее количество результатов
                      - `totalPages` - Общее количество страниц
                      - `number` - Номер текущей страницы
                      - `size` - Размер страницы
                      - `first` - Является ли страница первой
                      - `last` - Является ли страница последней
                    
                    **Примеры:**
                    - `/api/result?page=0&size=10` - Первая страница с 10 результатами
                    - `/api/result?page=1&size=20` - Вторая страница с 20 результатами
                    """
    )
    @ApiResponses(value = {
            @ApiResponse(
                    responseCode = "200",
                    description = "Список результатов успешно получен",
                    content = @Content(schema = @Schema(implementation = Page.class))
            ),
            @ApiResponse(
                    responseCode = "400",
                    description = "Неверные параметры пагинации (отрицательные значения)",
                    content = @Content
            ),
            @ApiResponse(
                    responseCode = "401",
                    description = "Не авторизован",
                    content = @Content
            )
    })
    @ResponseStatus(HttpStatus.OK)
    public Page<AnalysisResult> getAll(
            @Parameter(
                    description = "Номер страницы (начиная с 0)",
                    example = "0"
            )
            @RequestParam(defaultValue = "0") int page,
            @Parameter(
                    description = "Размер страницы",
                    example = "10"
            )
            @RequestParam(defaultValue = "10") int size) {
        return analysisResultUseCase.getAll(page, size);
    }

    @DeleteMapping(value = "/{id}", produces = MediaType.APPLICATION_JSON_VALUE)
    @Operation(
            summary = "Удалить результат анализа",
            description = """
                    Удаляет результат анализа по указанному ID.
                    
                    **Внимание:** Операция необратима. После удаления результат нельзя восстановить.
                    
                    **Параметры:**
                    - `id` - ID результата анализа для удаления
                    """
    )
    @ApiResponses(value = {
            @ApiResponse(
                    responseCode = "200",
                    description = "Результат успешно удален",
                    content = @Content
            ),
            @ApiResponse(
                    responseCode = "404",
                    description = "Результат анализа не найден",
                    content = @Content
            ),
            @ApiResponse(
                    responseCode = "401",
                    description = "Не авторизован",
                    content = @Content
            )
    })
    @ResponseStatus(HttpStatus.OK)
    public void delete(
            @Parameter(
                    description = "ID результата анализа для удаления",
                    required = true,
                    example = "507f1f77bcf86cd799439011"
            )
            @PathVariable String id) {
        analysisResultUseCase.delete(id);
    }
}
