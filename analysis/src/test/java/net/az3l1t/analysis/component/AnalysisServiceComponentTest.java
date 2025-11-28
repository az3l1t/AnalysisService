package net.az3l1t.analysis.component;

import com.fasterxml.jackson.databind.ObjectMapper;
import net.az3l1t.analysis.application.rest.client.EmiasClient;
import net.az3l1t.analysis.domain.port.out.MessagePublisherPort;
import net.az3l1t.analysis.infrastructure.adapter.in.rest.dto.in.CreateInResultDto;
import net.az3l1t.analysis.infrastructure.adapter.in.rest.dto.in.UpdateInResultDto;
import net.az3l1t.analysis.infrastructure.adapter.in.rest.dto.out.GetOutResultDto;
import net.az3l1t.analysis.infrastructure.adapter.out.artemis.dto.NotificationDto;
import net.az3l1t.analysis.infrastructure.adapter.out.artemis.dto.SendResultsDto;
import net.az3l1t.analysis.infrastructure.entity.AnalysisResultDocument;
import net.az3l1t.analysis.infrastructure.repository.AnalysisRepository;
import org.junit.jupiter.api.AfterEach;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.http.MediaType;
import org.springframework.test.context.ActiveProfiles;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;
import org.testcontainers.containers.MongoDBContainer;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;

import java.time.LocalDateTime;
import java.util.Map;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.doNothing;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.put;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@AutoConfigureMockMvc(addFilters = false)
@ActiveProfiles("test")
@Testcontainers
@DisplayName("КОМПОНЕНТНЫЕ ТЕСТЫ: Analysis Service (внешние зависимости замокированы)")
class AnalysisServiceComponentTest {

    @Container
    static MongoDBContainer mongoDBContainer = new MongoDBContainer("mongo:7.0")
            .withReuse(true);

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.data.mongodb.uri", mongoDBContainer::getReplicaSetUrl);
    }

    @Autowired
    private MockMvc mockMvc;

    @Autowired
    private ObjectMapper objectMapper;

    @Autowired
    private AnalysisRepository analysisRepository;

    // ВНЕШНИЕ ЗАВИСИМОСТИ - МОКИРУЮТСЯ (это ключевое отличие компонентных тестов)
    @MockBean
    private EmiasClient emiasClient;

    @MockBean
    private MessagePublisherPort messagePublisherPort;

    @BeforeEach
    void setUp() {
        doNothing().when(messagePublisherPort).publish(any(SendResultsDto.class));
        doNothing().when(messagePublisherPort).publishNotification(any(NotificationDto.class));
    }

    @AfterEach
    void tearDown() {
        analysisRepository.deleteAll();
    }

    @Test
    @DisplayName("Компонентный тест: создание результата анализа")
    void componentTest_CreateAnalysisResult() throws Exception {
        // Given
        CreateInResultDto createDto = new CreateInResultDto();
        createDto.setPatientId(100L);
        createDto.setDoctorId(200L);
        createDto.setResults(Map.of("hb", "12.5", "rbc", "4.5"));

        // When
        MvcResult result = mockMvc.perform(post("/api/result")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(createDto)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").exists())
                .andExpect(jsonPath("$.patientId").value(100))
                .andExpect(jsonPath("$.results.hb").value("12.5"))
                .andReturn();

        // Then - проверяем сохранение в БД (реальная БД, не мок)
        GetOutResultDto created = objectMapper.readValue(
                result.getResponse().getContentAsString(),
                GetOutResultDto.class
        );
        AnalysisResultDocument saved = analysisRepository.findById(created.getId())
                .orElseThrow();
        assertThat(saved.getPatientId()).isEqualTo(100L);
        assertThat(saved.getResults()).containsEntry("hb", "12.5");
    }

    @Test
    @DisplayName("Компонентный тест: получение результата по ID")
    void componentTest_GetAnalysisResultById() throws Exception {
        // Given
        String id = createTestResult(300L, 400L, Map.of("hb", "14.0"));

        // When & Then
        mockMvc.perform(get("/api/result/{id}", id))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value(id))
                .andExpect(jsonPath("$.patientId").value(300))
                .andExpect(jsonPath("$.results.hb").value("14.0"));
    }

    @Test
    @DisplayName("Компонентный тест: обновление результата (проверка отправки уведомления через мок)")
    void componentTest_UpdateAnalysisResult() throws Exception {
        // Given
        String id = createTestResult(500L, 600L, Map.of("hb", "12.0"));

        UpdateInResultDto updateDto = new UpdateInResultDto();
        updateDto.setId(id);
        updateDto.setResults(Map.of("hb", "13.5", "rbc", "4.8"));

        // When
        mockMvc.perform(put("/api/result")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(updateDto)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.results.hb").value("13.5"));

        // Then - проверяем обновление в БД
        AnalysisResultDocument updated = analysisRepository.findById(id).orElseThrow();
        assertThat(updated.getResults()).containsEntry("hb", "13.5");

        // Проверяем, что уведомление отправлено через мок (внешняя зависимость)
        verify(messagePublisherPort, times(1))
                .publishNotification(any(NotificationDto.class));
    }

    @Test
    @DisplayName("Компонентный тест: подтверждение результата (проверка отправки уведомления через мок)")
    void componentTest_ConfirmAnalysisResult() throws Exception {
        // Given
        String id = createTestResult(700L, 800L, Map.of("hb", "12.5"));
        
        // Проверяем, что результат создан и не подтвержден
        AnalysisResultDocument beforeConfirm = analysisRepository.findById(id)
                .orElseThrow(() -> new AssertionError("Result not found in database"));
        assertThat(beforeConfirm.getIsConfirmed()).isFalse();

        // When
        mockMvc.perform(put("/api/result/confirm/{id}", id))
                .andExpect(status().isOk());

        // Then - проверяем подтверждение в БД
        AnalysisResultDocument confirmed = analysisRepository.findById(id)
                .orElseThrow(() -> new AssertionError("Result not found after confirm"));
        assertThat(confirmed.getIsConfirmed()).isTrue();

        // Проверяем отправку уведомления через мок
        verify(messagePublisherPort, times(1))
                .publishNotification(any(NotificationDto.class));
    }

    @Test
    @DisplayName("Компонентный тест: удаление результата")
    void componentTest_DeleteAnalysisResult() throws Exception {
        // Given
        String id = createTestResult(900L, 1000L, Map.of("hb", "12.0"));
        assertThat(analysisRepository.findById(id)).isPresent();

        // When
        mockMvc.perform(delete("/api/result/{id}", id))
                .andExpect(status().isOk());

        // Then
        assertThat(analysisRepository.findById(id)).isEmpty();
    }

    @Test
    @DisplayName("Компонентный тест: получение результата из внешней системы (мок EmiasClient)")
    void componentTest_GetExternalResult() throws Exception {
        // Given - настраиваем мок внешнего сервиса
        String externalId = "external-123";
        SendResultsDto externalDto = new SendResultsDto(
                externalId,
                2000L,
                2100L,
                true,
                LocalDateTime.now(),
                Map.of("hb", "14.5")
        );
        when(emiasClient.getResultById(externalId)).thenReturn(externalDto);

        // When & Then
        mockMvc.perform(get("/api/result/external/{id}", externalId))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value(externalId))
                .andExpect(jsonPath("$.patientId").value(2000))
                .andExpect(jsonPath("$.isConfirmed").value(true))
                .andExpect(jsonPath("$.results.hb").value("14.5"));

        // Проверяем вызов мока внешнего сервиса
        verify(emiasClient, times(1)).getResultById(externalId);
    }

    @Test
    @DisplayName("Компонентный тест: полный цикл работы компонента")
    void componentTest_FullWorkflow() throws Exception {
        // Step 1: Создание
        String id = createTestResult(3000L, 3100L, Map.of("hb", "11.5"));

        // Step 2: Получение - проверяем через репозиторий, так как GET возвращает Optional
        AnalysisResultDocument created = analysisRepository.findById(id)
                .orElseThrow(() -> new AssertionError("Result not found after creation"));
        assertThat(created.getIsConfirmed()).isFalse();

        // Step 3: Обновление
        UpdateInResultDto updateDto = new UpdateInResultDto();
        updateDto.setId(id);
        updateDto.setResults(Map.of("hb", "13.0"));

        mockMvc.perform(put("/api/result")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(updateDto)))
                .andExpect(status().isOk());

        // Step 4: Подтверждение
        mockMvc.perform(put("/api/result/confirm/{id}", id))
                .andExpect(status().isOk());

        // Step 5: Проверка в БД
        AnalysisResultDocument result = analysisRepository.findById(id)
                .orElseThrow(() -> new AssertionError("Result not found after confirm"));
        assertThat(result.getIsConfirmed()).isTrue();
        assertThat(result.getResults()).containsEntry("hb", "13.0");

        // Проверяем взаимодействие с моками внешних зависимостей
        verify(messagePublisherPort, times(2))
                .publishNotification(any(NotificationDto.class));
    }

    /**
     * Вспомогательный метод для создания тестового результата.
     */
    private String createTestResult(Long patientId, Long doctorId, Map<String, String> results)
            throws Exception {
        CreateInResultDto createDto = new CreateInResultDto();
        createDto.setPatientId(patientId);
        createDto.setDoctorId(doctorId);
        createDto.setResults(results);

        MvcResult result = mockMvc.perform(post("/api/result")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(createDto)))
                .andExpect(status().isOk())
                .andReturn();

        GetOutResultDto created = objectMapper.readValue(
                result.getResponse().getContentAsString(),
                GetOutResultDto.class
        );
        return created.getId();
    }
}
