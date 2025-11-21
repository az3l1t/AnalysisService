package net.az3l1t.analysis.infrastructure.adapter.in.rest;

import com.fasterxml.jackson.databind.ObjectMapper;
import net.az3l1t.analysis.application.rest.client.EmiasClient;
import net.az3l1t.analysis.infrastructure.adapter.in.rest.dto.in.CreateInResultDto;
import net.az3l1t.analysis.infrastructure.adapter.in.rest.dto.in.UpdateInResultDto;
import net.az3l1t.analysis.infrastructure.adapter.in.rest.dto.out.GetOutResultDto;
import net.az3l1t.analysis.infrastructure.adapter.out.artemis.dto.SendResultsDto;
import net.az3l1t.analysis.infrastructure.entity.AnalysisResultDocument;
import net.az3l1t.analysis.infrastructure.repository.AnalysisRepository;
import org.junit.jupiter.api.AfterEach;
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
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@AutoConfigureMockMvc(addFilters = false)
@ActiveProfiles("test")
@Testcontainers
class ResultControllerIT {

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

    @MockBean
    private EmiasClient emiasClient;

    @AfterEach
    void cleanUp() {
        analysisRepository.deleteAll();
    }

    @Test
    void shouldCreateAndFetchResult() throws Exception {
        CreateInResultDto createDto = new CreateInResultDto();
        createDto.setPatientId(11L);
        createDto.setDoctorId(22L);
        createDto.setIsConfirmed(false);
        createDto.setResults(Map.of("hb", "12.1"));

        MvcResult creationResult = mockMvc.perform(post("/api/result")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(createDto)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.patientId").value(11))
                .andExpect(jsonPath("$.isConfirmed").value(false))
                .andReturn();

        GetOutResultDto created = objectMapper.readValue(
                creationResult.getResponse().getContentAsString(),
                GetOutResultDto.class
        );

        mockMvc.perform(get("/api/result/{id}", created.getId()))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value(created.getId()))
                .andExpect(jsonPath("$.results.hb").value("12.1"));

        mockMvc.perform(get("/api/result").param("page", "0").param("size", "5"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.content[0].id").value(created.getId()));
    }

    @Test
    void shouldUpdateConfirmAndDeleteResult() throws Exception {
        String id = createResult();

        UpdateInResultDto updateDto = new UpdateInResultDto();
        updateDto.setId(id);
        updateDto.setPatientId(33L);
        updateDto.setDoctorId(44L);
        updateDto.setIsConfirmed(true);
        updateDto.setResults(Map.of("hb", "13.4"));

        mockMvc.perform(put("/api/result")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(updateDto)))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.patientId").value(33))
                .andExpect(jsonPath("$.results.hb").value("13.4"));

        mockMvc.perform(put("/api/result/confirm/{id}", id))
                .andExpect(status().isOk());

        AnalysisResultDocument confirmed = analysisRepository.findById(id).orElseThrow();
        assertThat(confirmed.getIsConfirmed()).isTrue();

        mockMvc.perform(delete("/api/result/{id}", id))
                .andExpect(status().isOk());

        assertThat(analysisRepository.findById(id)).isEmpty();
    }

    @Test
    void shouldGetExternalResult() throws Exception {
        String id = createResult();
        
        SendResultsDto externalDto = new SendResultsDto(
                id, 1L, 2L, true, LocalDateTime.now(), Map.of("hb", "11.4")
        );
        when(emiasClient.getResultById(anyString())).thenReturn(externalDto);

        mockMvc.perform(get("/api/result/external/{id}", id))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value(id))
                .andExpect(jsonPath("$.isConfirmed").value(true));
    }

    private String createResult() throws Exception {
        CreateInResultDto createDto = new CreateInResultDto();
        createDto.setPatientId(1L);
        createDto.setDoctorId(2L);
        createDto.setIsConfirmed(false);
        createDto.setResults(Map.of("hb", "11.4"));

        MvcResult creationResult = mockMvc.perform(post("/api/result")
                        .contentType(MediaType.APPLICATION_JSON)
                        .content(objectMapper.writeValueAsString(createDto)))
                .andExpect(status().isOk())
                .andReturn();

        GetOutResultDto created = objectMapper.readValue(
                creationResult.getResponse().getContentAsString(),
                GetOutResultDto.class
        );
        return created.getId();
    }
}

